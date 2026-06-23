import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.memory_store import store


def _reload_for_v5e(monkeypatch: pytest.MonkeyPatch, *, external_runtime: str = "disabled") -> None:
    monkeypatch.setenv("AUTH_MODE", "anonymous_session")
    monkeypatch.setenv("REPORT_LLM_RUNTIME", "mock")
    monkeypatch.setenv("EXTERNAL_SOURCE_RUNTIME", external_runtime)
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")

    import app.core.config as config_module

    importlib.reload(config_module)
    for module_name in (
        "app.api.deps",
        "app.services.analysis_job_service",
        "app.services.external_source_service",
        "app.services.session_service",
    ):
        importlib.reload(importlib.import_module(module_name))


def _clear_store() -> None:
    store.inputs.clear()
    store.features.clear()
    store.embedding_records.clear()
    store.jobs.clear()
    store.reports.clear()
    store.report_metadata.clear()
    store.feedback.clear()
    store.analysis_logs.clear()
    store.profiles.clear()
    store.timeline_events.clear()
    store.timeline_dedupe_keys.clear()
    store.observation_sessions.clear()
    store.agent_action_logs.clear()
    store.external_import_batches.clear()
    store.external_context_items.clear()
    store.external_source_connections.clear()
    store.external_oauth_states.clear()
    store.user_sessions.clear()


def _client() -> TestClient:
    return TestClient(create_app())


def _bootstrap(client: TestClient) -> str:
    response = client.post("/api/session/bootstrap")
    assert response.status_code == 200
    return response.json()["userId"]


def _create_report(client: TestClient, *, prefix: str = "v5e") -> tuple[str, str, str, list[str]]:
    input_ids: list[str] = []
    for index in range(3):
        response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "contentText": f"{prefix} quiet structure sample {index}",
                "title": f"{prefix} sample {index}",
            },
        )
        assert response.status_code == 200
        input_ids.append(response.json()["id"])

    job_response = client.post("/api/analysis-jobs", json={"inputIds": input_ids})
    assert job_response.status_code == 200
    job = job_response.json()
    assert job["status"] == "completed"
    assert job["reportId"] is not None
    return job["userId"], job["id"], job["reportId"], input_ids


def test_v5e_cross_user_scope_blocks_core_and_debug_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_store()
    _reload_for_v5e(monkeypatch)
    client_a = _client()
    user_a = _bootstrap(client_a)
    _, job_id, report_id, _ = _create_report(client_a)

    client_b = _client()
    user_b = _bootstrap(client_b)
    assert user_a != user_b

    protected_paths = [
        f"/api/reports/{report_id}",
        f"/api/reports/{report_id}/evaluation",
        f"/api/reports/{report_id}/grouping-stability",
        f"/api/analysis-jobs/{job_id}",
        f"/api/analysis-jobs/{job_id}/debug",
        f"/api/analysis-jobs/{job_id}/failure-replay",
        f"/api/users/{user_a}/profile",
        f"/api/users/{user_a}/reports",
        f"/api/users/{user_a}/external-imports",
    ]
    for path in protected_paths:
        denied = client_b.get(path)
        assert denied.status_code == 403, path


def test_v5e_debug_and_evidence_boundaries_remain_visible(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_store()
    _reload_for_v5e(monkeypatch)
    client = _client()
    user_id = _bootstrap(client)
    _, job_id, report_id, input_ids = _create_report(client)

    debug_response = client.get(f"/api/analysis-jobs/{job_id}/debug")
    assert debug_response.status_code == 200
    debug = debug_response.json()
    assert debug["authContext"]["authMode"] == "anonymous_session"
    assert debug["authContext"]["resolvedUserId"] == user_id
    assert debug["authContext"]["sessionPresent"] is True

    mock_usage = {item["component"]: item for item in debug["mockUsage"]}
    assert mock_usage["MockInterpretationGenerator"]["status"] == "enabled"
    assert mock_usage["MockInterpretationGenerator"]["devOnly"] is True
    assert debug["boundaryWarnings"]
    assert debug["retrievalTrace"]

    report_response = client.get(f"/api/reports/{report_id}")
    assert report_response.status_code == 200
    report = report_response.json()
    allowed_refs = set(input_ids)
    for insight in report["insights"]:
        assert insight["evidenceRefs"]
        assert set(insight["evidenceRefs"]) <= allowed_refs
        combined = " ".join(
            str(insight.get(key, ""))
            for key in ("title", "observation", "interpretation", "uncertainty")
        )
        banned_diagnostic_phrases = (
            "人格诊断为",
            "心理问题",
            "心理疾病",
            "能力强",
            "能力弱",
            "命运",
            "说明你是",
        )
        assert all(phrase not in combined for phrase in banned_diagnostic_phrases)


def test_v5e_external_import_remains_supplementary_until_confirmed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_store()
    _reload_for_v5e(monkeypatch, external_runtime="mock_oauth")
    client = _client()
    user_id = _bootstrap(client)

    connect_response = client.post(f"/api/users/{user_id}/external-sources/demo_notes/connect")
    assert connect_response.status_code == 200
    callback_response = client.get(connect_response.json()["authorizationUrl"])
    assert callback_response.status_code == 200
    assert "accessToken" not in callback_response.json()
    assert "refreshToken" not in callback_response.json()

    preview_response = client.post(
        f"/api/users/{user_id}/external-sources/demo_notes/imports/preview",
        json={"limit": 2},
    )
    assert preview_response.status_code == 200
    pending_batch = preview_response.json()
    assert pending_batch["status"] == "pending_confirmation"

    profile_before_confirm = client.get(f"/api/users/{user_id}/profile")
    assert profile_before_confirm.status_code == 200
    assert profile_before_confirm.json()["profile"] is None

    confirm_response = client.post(f"/api/users/{user_id}/external-imports/{pending_batch['id']}/confirm")
    assert confirm_response.status_code == 200
    confirmed_batch = confirm_response.json()
    assert confirmed_batch["status"] == "confirmed"

    profile_after_confirm = client.get(f"/api/users/{user_id}/profile")
    assert profile_after_confirm.status_code == 200
    assert profile_after_confirm.json()["profile"] is None

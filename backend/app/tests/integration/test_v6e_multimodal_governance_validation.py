import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repositories.memory_store import store


def _reload_for_v6e(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_MODE", "anonymous_session")
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")
    monkeypatch.setenv("REPORT_LLM_RUNTIME", "mock")
    monkeypatch.setenv("IMAGE_FEATURE_RUNTIME", "mock")
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "metadata_only")
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "metadata_only")
    monkeypatch.setenv("EXTERNAL_SOURCE_RUNTIME", "disabled")

    import app.core.config as config_module

    importlib.reload(config_module)
    for module_name in (
        "app.api.deps",
        "app.ai.factory",
        "app.services.analysis_job_service",
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


def _client(*, raise_server_exceptions: bool = True) -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=raise_server_exceptions)


def _bootstrap(client: TestClient) -> str:
    response = client.post("/api/session/bootstrap")
    assert response.status_code == 200
    return response.json()["userId"]


def _create_multimodal_report(client: TestClient) -> tuple[str, str, str, list[str], str]:
    upload_response = client.post(
        "/api/files/upload",
        files={"file": ("sample.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )
    assert upload_response.status_code == 200
    uploaded_file_url = upload_response.json()["fileUrl"]
    file_id = upload_response.json()["fileId"]

    payloads = [
        {
            "type": "image",
            "title": "quiet uploaded image",
            "fileUrl": uploaded_file_url,
            "description": "user uploaded image metadata",
        },
        {
            "type": "music",
            "title": "ambient track",
            "fileUrl": "https://example.com/track",
            "description": "metadata-only music reference",
        },
        {
            "type": "video",
            "title": "slow clip",
            "fileUrl": "https://example.com/video",
            "description": "metadata-only video reference",
        },
        {
            "type": "text",
            "title": "quiet room note",
            "contentText": "房间里只剩下安静的光和缓慢的回声。",
        },
    ]
    input_ids: list[str] = []
    for payload in payloads:
        response = client.post("/api/inputs", json=payload)
        assert response.status_code == 200
        input_ids.append(response.json()["id"])

    job_response = client.post("/api/analysis-jobs", json={"inputIds": input_ids})
    assert job_response.status_code == 200
    job = job_response.json()
    assert job["status"] == "completed"
    assert job["reportId"] is not None
    return job["userId"], job["id"], job["reportId"], input_ids, file_id


def test_v6e_multimodal_runtime_boundaries_and_evidence_are_traceable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_store()
    _reload_for_v6e(monkeypatch)
    client = _client()
    user_id = _bootstrap(client)
    _, job_id, report_id, input_ids, _file_id = _create_multimodal_report(client)

    debug_response = client.get(f"/api/analysis-jobs/{job_id}/debug")
    assert debug_response.status_code == 200
    debug = debug_response.json()
    assert debug["authContext"]["resolvedUserId"] == user_id

    mock_usage = {item["component"]: item for item in debug["mockUsage"]}
    assert mock_usage["MockImageFeatureExtractor"]["status"] == "enabled"
    assert mock_usage["MockImageFeatureExtractor"]["devOnly"] is True
    assert mock_usage["MetadataOnlyAudioMusicFeatureExtractor"]["status"] == "disabled"
    assert mock_usage["MetadataOnlyVideoFeatureExtractor"]["status"] == "disabled"
    assert "metadata only" in mock_usage["MetadataOnlyAudioMusicFeatureExtractor"]["developerMessage"]
    assert "metadata only" in mock_usage["MetadataOnlyVideoFeatureExtractor"]["developerMessage"]

    runtime_boundary = next(
        warning for warning in debug["boundaryWarnings"] if warning["capability"] == "Real vision / LLM runtime"
    )
    boundary_message = runtime_boundary["developerMessage"]
    assert "IMAGE_FEATURE_RUNTIME=mock" in boundary_message
    assert "MUSIC_FEATURE_RUNTIME=metadata_only" in boundary_message
    assert "VIDEO_FEATURE_RUNTIME=metadata_only" in boundary_message

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
        banned_phrases = ("人格诊断为", "心理问题", "心理疾病", "能力强", "能力弱", "命运", "说明你是")
        assert all(phrase not in combined for phrase in banned_phrases)

    features = {feature["featureType"]: feature for feature in report["lowLevelFeatures"]}
    assert features["image"]["lowLevelFeatures"]["imageParsingStatus"]["value"] == "placeholder"
    assert features["music"]["lowLevelFeatures"]["musicParsingStatus"]["value"] == "metadata_only"
    assert features["video"]["lowLevelFeatures"]["videoParsingStatus"]["value"] == "metadata_only"


def test_v6e_profile_requires_feedback_before_multimodal_evidence_becomes_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_store()
    _reload_for_v6e(monkeypatch)
    client = _client()
    user_id = _bootstrap(client)
    _, _job_id, report_id, input_ids, _file_id = _create_multimodal_report(client)

    profile_before = client.get(f"/api/users/{user_id}/profile")
    assert profile_before.status_code == 200
    before_profile = profile_before.json()["profile"]
    if before_profile is not None:
        feature_only_items = [
            item
            for item in before_profile["items"]
            if item["evidence"] and all(evidence["evidenceType"] == "feature" for evidence in item["evidence"])
        ]
        assert all(item["status"] != "stable" for item in feature_only_items)

    report = client.get(f"/api/reports/{report_id}").json()
    insight_id = report["insights"][0]["insightId"]
    feedback_response = client.post(f"/api/insights/{insight_id}/feedback", json={"rating": "somewhat_me"})
    assert feedback_response.status_code == 200
    feedback_id = feedback_response.json()["id"]

    profile_after = client.get(f"/api/users/{user_id}/profile")
    assert profile_after.status_code == 200
    profile = profile_after.json()["profile"]
    assert profile is not None
    evidence_records = [
        evidence
        for item in profile["items"]
        for evidence in item["evidence"]
    ]
    assert evidence_records
    feedback_evidence = [
        evidence
        for evidence in evidence_records
        if evidence["evidenceType"] == "feedback" and evidence["evidenceId"] == feedback_id
    ]
    assert feedback_evidence
    assert all(evidence["evidenceId"] not in input_ids for evidence in evidence_records)


def test_v6e_cross_user_scope_blocks_multimodal_report_debug_profile_and_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_store()
    _reload_for_v6e(monkeypatch)
    client_a = _client()
    user_a = _bootstrap(client_a)
    _, job_id, report_id, _input_ids, file_id = _create_multimodal_report(client_a)

    client_b = _client()
    user_b = _bootstrap(client_b)
    assert user_a != user_b

    protected_paths = [
        f"/api/reports/{report_id}",
        f"/api/analysis-jobs/{job_id}",
        f"/api/analysis-jobs/{job_id}/debug",
        f"/api/users/{user_a}/profile",
    ]
    for path in protected_paths:
        denied = client_b.get(path)
        assert denied.status_code == 403, path

    file_denied = client_b.get(f"/api/files/{file_id}")
    assert file_denied.status_code == 404


def test_v6e_disabled_multimodal_runtime_fails_fast_without_silent_mock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_store()
    _reload_for_v6e(monkeypatch)
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "disabled")
    client = _client(raise_server_exceptions=False)
    _bootstrap(client)

    music_response = client.post(
        "/api/inputs",
        json={
            "type": "music",
            "title": "disabled music",
            "fileUrl": "https://example.com/track",
        },
    )
    assert music_response.status_code == 200
    text_ids: list[str] = []
    for index in range(2):
        text_response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "title": f"quiet text {index}",
                "contentText": f"安静的文本样本 {index}",
            },
        )
        assert text_response.status_code == 200
        text_ids.append(text_response.json()["id"])

    job_response = client.post(
        "/api/analysis-jobs",
        json={"inputIds": [music_response.json()["id"], *text_ids]},
    )
    assert job_response.status_code == 500
    assert not store.reports

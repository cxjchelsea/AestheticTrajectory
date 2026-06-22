import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _bootstrap_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AUTH_MODE", "anonymous_session")
    import app.core.config as config_module

    importlib.reload(config_module)
    importlib.reload(importlib.import_module("app.api.deps"))
    return TestClient(app)


def _create_report(client: TestClient) -> tuple[str, str]:
    input_ids: list[str] = []
    for index in range(3):
        input_response = client.post(
            "/api/inputs",
            json={"type": "text", "contentText": f"scoped sample {index}", "title": f"scoped {index}"},
        )
        assert input_response.status_code == 200
        input_ids.append(input_response.json()["id"])

    job_response = client.post("/api/analysis-jobs", json={"inputIds": input_ids})
    assert job_response.status_code == 200
    job = job_response.json()
    assert job["reportId"] is not None
    return job["userId"], job["reportId"]


def test_session_bootstrap_creates_persistent_user(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _bootstrap_client(monkeypatch)

    first = client.post("/api/session/bootstrap")
    assert first.status_code == 200
    first_body = first.json()
    assert first_body["authMode"] == "anonymous_session"
    assert first_body["userId"].startswith("user_")
    assert first_body["sessionToken"]

    second = client.post("/api/session/bootstrap")
    assert second.status_code == 200
    second_body = second.json()
    assert second_body["userId"] == first_body["userId"]


def test_cross_user_profile_access_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    client_a = _bootstrap_client(monkeypatch)
    user_a = client_a.post("/api/session/bootstrap").json()["userId"]

    client_b = _bootstrap_client(monkeypatch)
    user_b = client_b.post("/api/session/bootstrap").json()["userId"]
    assert user_a != user_b

    denied = client_a.get(f"/api/users/{user_b}/profile")
    assert denied.status_code == 403


def test_cross_user_report_access_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    client_a = _bootstrap_client(monkeypatch)
    client_a.post("/api/session/bootstrap")
    _, report_id = _create_report(client_a)

    client_b = _bootstrap_client(monkeypatch)
    client_b.post("/api/session/bootstrap")

    denied = client_b.get(f"/api/reports/{report_id}")
    assert denied.status_code == 403


def test_dev_mode_keeps_user_anonymous_baseline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_MODE", "dev")
    import app.core.config as config_module

    importlib.reload(config_module)
    importlib.reload(importlib.import_module("app.api.deps"))
    importlib.reload(importlib.import_module("app.services.session_service"))

    client = TestClient(app)
    bootstrap = client.post("/api/session/bootstrap")
    assert bootstrap.status_code == 200
    assert bootstrap.json()["userId"] == "user_anonymous"
    assert bootstrap.json()["authMode"] == "dev"

    me = client.get("/api/session/me")
    assert me.status_code == 200
    assert me.json()["userId"] == "user_anonymous"
    assert me.json()["authMode"] == "dev"

    profile = client.get("/api/users/user_anonymous/profile")
    assert profile.status_code == 200


def test_dev_mode_history_matches_analysis_user(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_MODE", "dev")
    import app.core.config as config_module

    importlib.reload(config_module)
    importlib.reload(importlib.import_module("app.api.deps"))
    importlib.reload(importlib.import_module("app.services.session_service"))

    client = TestClient(app)
    client.post("/api/session/bootstrap")
    user_id, _report_id = _create_report(client)
    assert user_id == "user_anonymous"

    history = client.get("/api/users/user_anonymous/reports")
    assert history.status_code == 200
    assert history.json()["total"] >= 1

import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def _reload_external_source_modules() -> None:
    import app.core.config as config_module

    importlib.reload(config_module)
    importlib.reload(importlib.import_module("app.services.external_source_service"))
    importlib.reload(importlib.import_module("app.api.deps"))


def test_v5c_mock_oauth_preview_requires_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXTERNAL_SOURCE_RUNTIME", "mock_oauth")
    _reload_external_source_modules()
    client = TestClient(create_app())

    connect_response = client.post("/api/users/user_anonymous/external-sources/demo_notes/connect")
    assert connect_response.status_code == 200
    authorization_url = connect_response.json()["authorizationUrl"]
    assert "state=" in authorization_url

    callback_response = client.get(authorization_url)
    assert callback_response.status_code == 200
    connection = callback_response.json()
    assert connection["status"] == "connected"
    assert "accessToken" not in connection
    assert "refreshToken" not in connection

    preview_response = client.post(
        "/api/users/user_anonymous/external-sources/demo_notes/imports/preview",
        json={"limit": 2},
    )
    assert preview_response.status_code == 200
    batch = preview_response.json()
    assert batch["status"] == "pending_confirmation"
    assert batch["itemCount"] == 2
    assert batch["sourceSystem"] == "demo_notes"

    imports_response = client.get("/api/users/user_anonymous/external-imports")
    assert imports_response.status_code == 200
    assert imports_response.json()["batches"][0]["status"] == "pending_confirmation"

    confirm_response = client.post(f"/api/users/user_anonymous/external-imports/{batch['id']}/confirm")
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "confirmed"


def test_v5c_disabled_runtime_fails_fast() -> None:
    client = TestClient(create_app())

    response = client.post("/api/users/user_anonymous/external-sources/demo_notes/connect")

    assert response.status_code == 400
    assert "EXTERNAL_SOURCE_RUNTIME=disabled" in response.json()["detail"]


def test_v5c_external_source_uses_user_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EXTERNAL_SOURCE_RUNTIME", "mock_oauth")
    monkeypatch.setenv("AUTH_MODE", "anonymous_session")
    _reload_external_source_modules()
    client = TestClient(create_app())
    current_user = client.post("/api/session/bootstrap").json()["userId"]
    assert current_user != "user_other"

    response = client.post("/api/users/user_other/external-sources/demo_notes/connect")

    assert response.status_code == 403

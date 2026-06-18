from fastapi.testclient import TestClient

from app.main import create_app


def test_observation_api_abstains_without_reports() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/users/user_observation_empty/observations",
        json={"triggerSource": "test", "period": "week"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "abstained"


def test_external_import_confirm_flow() -> None:
    client = TestClient(create_app())
    create_response = client.post(
        "/api/users/user_anonymous/external-imports",
        json={
            "sourceSystem": "mock_notes",
            "items": [
                {
                    "title": "笔记：低饱和",
                    "snippet": "外部笔记片段",
                    "sourceUri": "https://example.com/note/1",
                    "tags": ["note"],
                }
            ],
        },
    )
    assert create_response.status_code == 200
    batch_id = create_response.json()["id"]
    assert create_response.json()["status"] == "pending_confirmation"

    confirm_response = client.post(f"/api/users/user_anonymous/external-imports/{batch_id}/confirm")
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "confirmed"


def test_agent_actions_api_lists_tool_trace() -> None:
    client = TestClient(create_app())
    session_response = client.post(
        "/api/users/user_observation_empty/observations",
        json={"triggerSource": "api_test", "period": "week"},
    )
    session_id = session_response.json()["id"]

    actions_response = client.get(
        f"/api/users/user_observation_empty/agent-actions?sessionId={session_id}"
    )
    assert actions_response.status_code == 200
    payload = actions_response.json()
    assert payload["total"] >= 1
    assert payload["actions"][0]["toolName"] == "list_reports"

from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.common import utc_now


def test_grouping_stability_api_returns_score() -> None:
    client = TestClient(create_app())
    input_ids = []
    for index in range(3):
        create_response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "contentText": f"quiet minimal room {index}",
                "source": "test",
                "title": f"Quiet room {index}",
            },
        )
        assert create_response.status_code == 200
        input_ids.append(create_response.json()["id"])

    job_response = client.post("/api/analysis-jobs", json={"inputIds": input_ids})
    assert job_response.status_code == 200
    report_id = job_response.json()["reportId"]

    response = client.get(f"/api/reports/{report_id}/grouping-stability")

    assert response.status_code == 200
    payload = response.json()
    assert payload["score"] == 1.0
    assert payload["pairCount"] == 3
    assert "长期偏好" in payload["disclaimer"]


def test_failure_replay_api_and_debug_extensions() -> None:
    client = TestClient(create_app())
    input_ids = []
    for index in range(3):
        create_response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "contentText": f"sample {index}",
                "source": "test",
                "title": f"sample {index}",
            },
        )
        assert create_response.status_code == 200
        input_ids.append(create_response.json()["id"])

    job_response = client.post("/api/analysis-jobs", json={"inputIds": input_ids})
    assert job_response.status_code == 200
    job_id = job_response.json()["id"]

    replay_response = client.get(f"/api/analysis-jobs/{job_id}/failure-replay")
    debug_response = client.get(f"/api/analysis-jobs/{job_id}/debug")

    assert replay_response.status_code == 200
    payload = replay_response.json()
    assert payload["failed"] is False
    assert payload["steps"]
    assert "只读回放" in payload["replayDisclaimer"]

    debug_payload = debug_response.json()
    assert debug_payload["groupingStabilityTrace"]["score"] == 1.0
    assert debug_payload["failureReplay"]["jobId"] == job_id
    agent_warning = next(
        item for item in debug_payload["boundaryWarnings"] if item["capability"] == "Agent / MCP runtime"
    )
    assert agent_warning["status"] == "dev_only"

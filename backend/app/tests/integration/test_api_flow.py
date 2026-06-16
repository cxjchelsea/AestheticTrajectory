from fastapi.testclient import TestClient

from app.main import app


def test_v1_api_flow_creates_report_and_feedback() -> None:
    client = TestClient(app)

    health_response = client.get("/api/health")
    assert health_response.status_code == 200

    input_ids: list[str] = []
    for index in range(3):
        response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "contentText": f"sample {index}",
                "title": f"sample {index}",
            },
        )
        assert response.status_code == 200
        input_ids.append(response.json()["id"])

    job_response = client.post("/api/analysis-jobs", json={"inputIds": input_ids})
    assert job_response.status_code == 200
    job = job_response.json()
    assert job["status"] == "completed"
    assert job["reportId"] is not None

    report_response = client.get(f"/api/reports/{job['reportId']}")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["insights"]
    assert report["insights"][0]["evidenceRefs"]

    history_response = client.get("/api/users/user_anonymous/reports")
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total"] >= 1
    assert history["reports"][0]["reportId"] == job["reportId"]
    assert history["reports"][0]["inputCount"] == 3

    feedback_response = client.post(
        f"/api/insights/{report['insights'][0]['insightId']}/feedback",
        json={"rating": "somewhat_me", "comment": "validation test"},
    )
    assert feedback_response.status_code == 200
    feedback = feedback_response.json()
    assert feedback["insightId"] == report["insights"][0]["insightId"]

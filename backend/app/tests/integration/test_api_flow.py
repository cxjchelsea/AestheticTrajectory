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

    debug_response = client.get(f"/api/analysis-jobs/{job['id']}/debug")
    assert debug_response.status_code == 200
    debug = debug_response.json()
    assert debug["jobId"] == job["id"]
    assert {step["stepId"] for step in debug["workflowTrace"]} >= {
        "extract_features",
        "generate_embeddings",
        "write_vectors",
        "cluster_inputs",
        "generate_report",
        "save_report",
    }
    assert debug["mockUsage"]
    assert debug["schemaValidation"]
    assert debug["boundaryWarnings"]

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

    profile_response = client.get("/api/users/user_anonymous/profile")
    assert profile_response.status_code == 200
    profile_payload = profile_response.json()
    assert profile_payload["profile"] is not None
    assert profile_payload["profile"]["items"]
    assert profile_payload["profile"]["items"][0]["evidence"]

    feedback_response = client.post(
        f"/api/insights/{report['insights'][0]['insightId']}/feedback",
        json={"rating": "somewhat_me", "comment": "validation test"},
    )
    assert feedback_response.status_code == 200
    feedback = feedback_response.json()
    assert feedback["insightId"] == report["insights"][0]["insightId"]

    updated_profile_response = client.get("/api/users/user_anonymous/profile")
    assert updated_profile_response.status_code == 200
    updated_profile = updated_profile_response.json()["profile"]
    assert any(
        evidence["evidenceType"] == "feedback"
        for item in updated_profile["items"]
        for evidence in item["evidence"]
    )

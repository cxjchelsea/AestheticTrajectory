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
        "retrieve_personal_history",
        "retrieve_aesthetic_knowledge",
        "generate_interpretations",
        "generate_report",
        "compute_report_evaluation",
        "save_report",
    }
    assert debug["mockUsage"]
    assert debug["schemaValidation"]
    assert debug["boundaryWarnings"]
    assert debug["retrievalTrace"]
    assert len(debug["retrievalTrace"]) == 2
    assert debug["contextAssemblyTrace"] is not None
    assert debug["evaluationTrace"] is not None
    assert debug["evaluationTrace"]["metrics"]["evidenceCoverage"] == 1.0

    report_response = client.get(f"/api/reports/{job['reportId']}")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["insights"]
    assert report["insights"][0]["evidenceRefs"]
    assert report.get("historyContext") is not None
    assert report["historyContext"]["message"] == "暂无可参考的历史报告。"
    assert report.get("knowledgeContext") is not None
    assert report["knowledgeContext"]["items"]
    assert all(item["sourceRefs"] for item in report["knowledgeContext"]["items"])
    assert report.get("evaluationMetrics") is not None
    assert report["evaluationMetrics"]["evidenceCoverage"] == 1.0

    evaluation_response = client.get(f"/api/reports/{job['reportId']}/evaluation")
    assert evaluation_response.status_code == 200
    evaluation = evaluation_response.json()
    assert evaluation["reportId"] == job["reportId"]
    assert evaluation["metrics"]["unsupportedInsightCount"] == 0
    assert "人格" not in evaluation["summary"]

    history_response = client.get("/api/users/user_anonymous/reports")
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total"] >= 1
    assert history["reports"][0]["reportId"] == job["reportId"]
    assert history["reports"][0]["inputCount"] == 3

    second_input_ids: list[str] = []
    for index in range(3):
        response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "contentText": f"comparison sample {index}",
                "title": f"comparison sample {index}",
            },
        )
        assert response.status_code == 200
        second_input_ids.append(response.json()["id"])

    second_job_response = client.post("/api/analysis-jobs", json={"inputIds": second_input_ids})
    assert second_job_response.status_code == 200
    second_job = second_job_response.json()
    assert second_job["reportId"] is not None

    second_report_response = client.get(f"/api/reports/{second_job['reportId']}")
    assert second_report_response.status_code == 200
    second_report = second_report_response.json()
    assert second_report["historyContext"] is not None
    assert second_report["historyContext"]["items"]
    assert any(item["sourceType"] == "report" for item in second_report["historyContext"]["items"])
    assert all(item["sourceRefs"] for item in second_report["historyContext"]["items"])

    comparison_response = client.get("/api/users/user_anonymous/reports/comparison/latest")
    assert comparison_response.status_code == 200
    comparison = comparison_response.json()
    assert comparison["currentReport"]["reportId"] == second_job["reportId"]
    assert comparison["previousReport"]["reportId"] == job["reportId"]
    assert comparison["featureChanges"]
    assert all(change["evidenceRefs"] for change in comparison["featureChanges"])
    assert "人格" not in comparison["summary"]
    assert "心理" not in comparison["summary"]
    assert "能力" not in comparison["summary"]

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

    current_feedback_response = client.get(f"/api/insights/{report['insights'][0]['insightId']}/feedback")
    assert current_feedback_response.status_code == 200
    assert current_feedback_response.json()["rating"] == "somewhat_me"

    revised_feedback_response = client.post(
        f"/api/insights/{report['insights'][0]['insightId']}/feedback",
        json={"rating": "not_me", "comment": "revised validation test"},
    )
    assert revised_feedback_response.status_code == 200
    revised_feedback = revised_feedback_response.json()
    assert revised_feedback["id"] == feedback["id"]
    assert revised_feedback["rating"] == "not_me"

    updated_profile_response = client.get("/api/users/user_anonymous/profile")
    assert updated_profile_response.status_code == 200
    updated_profile = updated_profile_response.json()["profile"]
    feedback_evidence = [
        evidence
        for item in updated_profile["items"]
        for evidence in item["evidence"]
        if evidence["evidenceType"] == "feedback" and evidence["evidenceId"] == revised_feedback["id"]
    ]
    assert len(feedback_evidence) == 1
    assert feedback_evidence[0]["direction"] == "negative"

    missing_feedback_response = client.post(
        "/api/insights/insight_missing/feedback",
        json={"rating": "not_me", "comment": "should fail"},
    )
    assert missing_feedback_response.status_code == 404

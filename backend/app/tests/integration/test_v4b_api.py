from fastapi.testclient import TestClient

from app.main import app


def test_timeline_api_returns_events_after_multiple_analyses() -> None:
    client = TestClient(app)

    for index in range(3):
        input_ids: list[str] = []
        for sample in range(3):
            text_response = client.post(
                "/api/inputs",
                json={
                    "type": "text",
                    "contentText": f"timeline sample {index}-{sample}",
                    "title": f"timeline sample {index}-{sample}",
                },
            )
            assert text_response.status_code == 200
            input_ids.append(text_response.json()["id"])
        job_response = client.post(
            "/api/analysis-jobs",
            json={"inputIds": input_ids},
        )
        assert job_response.status_code == 200
        assert job_response.json()["status"] == "completed"

    timeline_response = client.get("/api/users/user_anonymous/timeline")
    assert timeline_response.status_code == 200
    timeline = timeline_response.json()
    assert timeline["total"] >= 3
    assert timeline["events"]
    assert all(event["evidence"]["evidenceRefs"] for event in timeline["events"])
    assert "不是人格" in timeline["disclaimer"]
    for event in timeline["events"]:
        assert "人格" not in event["title"]
        assert "心理" not in event["title"]

    summary_response = client.get("/api/users/user_anonymous/timeline/summary?period=month")
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["eventCount"] >= 3
    assert summary["summaryText"]
    assert "心理" not in summary["summaryText"]


def test_feedback_not_me_creates_decline_timeline_event() -> None:
    client = TestClient(app)

    input_ids: list[str] = []
    for sample in range(3):
        text_response = client.post(
            "/api/inputs",
            json={
                "type": "text",
                "contentText": f"decline path {sample}",
                "title": f"decline path {sample}",
            },
        )
        input_ids.append(text_response.json()["id"])
    job_response = client.post(
        "/api/analysis-jobs",
        json={"inputIds": input_ids},
    )
    assert job_response.status_code == 200
    report_response = client.get(f"/api/reports/{job_response.json()['reportId']}")
    insight_id = report_response.json()["insights"][0]["insightId"]

    feedback_response = client.post(
        f"/api/insights/{insight_id}/feedback",
        json={"rating": "not_me", "comment": "不像我"},
    )
    assert feedback_response.status_code == 200

    timeline_response = client.get("/api/users/user_anonymous/timeline")
    timeline = timeline_response.json()
    decline_events = [event for event in timeline["events"] if event["eventType"] == "interpretation_decline"]
    assert decline_events
    assert decline_events[0]["relatedFeedbackIds"]

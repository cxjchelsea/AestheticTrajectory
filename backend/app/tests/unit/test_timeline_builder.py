from datetime import datetime, timezone

from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.report import Insight, ReportResponse
from app.schemas.timeline import TimelineEvidence
from app.services.report_comparison import build_latest_report_comparison
from app.services.timeline_builder import build_feedback_decline_event, build_timeline_events_for_report


def _report(report_id: str, feature_value: str, interpretation: str) -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title=f"report {report_id}",
        summary="summary",
        lowLevelFeatures=[
            {
                "inputId": "input_001",
                "featureType": "text",
                "lowLevelFeatures": {
                    "saturation": {"value": feature_value, "confidence": 0.8, "evidence": ["e1"]},
                },
                "sampleEvidence": ["e1"],
                "promptVersion": "v1",
                "modelName": "mock",
            }
        ],
        similarityGroups=[],
        possibleInterpretations=[
            {
                "id": "interp_001",
                "name": interpretation,
                "confidence": 0.6,
                "evidenceRefs": [report_id],
                "uncertainty": "uncertain",
            }
        ],
        insights=[
            Insight(
                insightId=f"insight_{report_id}",
                title=interpretation,
                observation="obs",
                evidenceRefs=[report_id],
                interpretation="interp",
                uncertainty="uncertain",
                confidence=0.5,
            )
        ],
        disclaimer="disclaimer",
    )


def test_timeline_builder_emits_report_completed_event() -> None:
    report = _report("report_001", "low", "冷感空间")
    occurred_at = datetime(2026, 6, 18, tzinfo=timezone.utc)

    drafts = build_timeline_events_for_report("user_a", report, occurred_at, [report])

    assert any(draft.event_type == "report_completed" for draft in drafts)


def test_timeline_builder_derives_comparison_events() -> None:
    previous = _report("report_prev", "low", "冷感空间")
    current = _report("report_curr", "high", "暖色结构")
    occurred_at = datetime(2026, 6, 18, tzinfo=timezone.utc)

    drafts = build_timeline_events_for_report("user_a", current, occurred_at, [current, previous])

    event_types = {draft.event_type for draft in drafts}
    assert "feature_shift" in event_types or "new_interpretation" in event_types


def test_feedback_decline_event_is_idempotent_by_dedupe_key() -> None:
    feedback = InsightFeedbackResponse(
        id="feedback_001",
        userId="user_a",
        insightId="insight_001",
        interpretationId=None,
        rating="not_me",
        comment="不像我",
        createdAt=datetime(2026, 6, 18, tzinfo=timezone.utc),
    )

    draft = build_feedback_decline_event(
        "user_a",
        feedback,
        "冷感空间",
        "report_001",
        feedback.created_at,
    )

    assert draft is not None
    assert draft.event_type == "interpretation_decline"
    assert draft.evidence.dedupe_key == "user_a:feedback:insight_001:interpretation_decline"


def test_report_comparison_still_compatible_with_timeline_builder() -> None:
    previous = _report("report_prev", "low", "冷感空间")
    current = _report("report_curr", "high", "暖色结构")
    comparison = build_latest_report_comparison("user_a", [current, previous])
    assert comparison.feature_changes

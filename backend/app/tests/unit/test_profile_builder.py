from datetime import timedelta

from app.schemas.common import utc_now
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.report import Insight, ReportResponse
from app.services.profile_builder import build_profile_from_sources


def test_feedback_ratings_map_to_profile_evidence_weights() -> None:
    report = _report("insight_001", "冷感空间偏好")
    feedback = [
        _feedback("feedback_very", "insight_001", "very_me"),
        _feedback("feedback_somewhat", "insight_001", "somewhat_me"),
        _feedback("feedback_unsure", "insight_001", "unsure"),
    ]

    profile = build_profile_from_sources("user_001", [report], feedback)

    assert profile.profile is not None
    item = profile.profile.items[0]
    evidence_by_id = {evidence.evidence_id: evidence for evidence in item.evidence}
    assert evidence_by_id["feedback_very"].direction == "positive"
    assert evidence_by_id["feedback_very"].weight_delta == 0.4
    assert evidence_by_id["feedback_somewhat"].direction == "positive"
    assert evidence_by_id["feedback_somewhat"].weight_delta == 0.2
    assert evidence_by_id["feedback_unsure"].direction == "uncertain"
    assert evidence_by_id["feedback_unsure"].weight_delta == 0.0
    assert item.status == "stable"
    assert item.weight == 0.6


def test_not_me_creates_rejected_item_and_is_excluded_from_positive_summary() -> None:
    report = _report("insight_001", "工业化孤独感")
    feedback = [_feedback("feedback_negative", "insight_001", "not_me")]

    profile = build_profile_from_sources("user_001", [report], feedback)

    assert profile.profile is not None
    item = profile.profile.items[0]
    assert item.status == "rejected"
    assert item.weight < 0
    assert item.evidence[0].direction == "negative"
    assert "工业化孤独感" not in profile.profile.summary
    assert "尚未形成正向轻量画像" in profile.profile.summary


def test_conflicting_feedback_keeps_traceable_evidence_without_stable_status() -> None:
    report = _report("insight_001", "冷感空间偏好")
    feedback = [
        _feedback("feedback_positive", "insight_001", "somewhat_me"),
        _feedback("feedback_negative", "insight_001", "not_me"),
    ]

    profile = build_profile_from_sources("user_001", [report], feedback)

    assert profile.profile is not None
    item = profile.profile.items[0]
    assert item.status == "rejected"
    assert item.weight == -0.3
    assert {evidence.direction for evidence in item.evidence} == {"positive", "negative"}
    assert "冷感空间偏好" not in profile.profile.summary


def test_unsure_only_item_remains_uncertain_and_does_not_strengthen_summary() -> None:
    report = _report("insight_001", "复古怀旧感")
    feedback = [_feedback("feedback_unsure", "insight_001", "unsure")]

    profile = build_profile_from_sources("user_001", [report], feedback)

    assert profile.profile is not None
    item = profile.profile.items[0]
    assert item.status == "uncertain"
    assert item.weight == 0
    assert item.evidence[0].direction == "uncertain"
    assert "复古怀旧感" not in profile.profile.summary


def test_duplicate_mock_insight_ids_do_not_duplicate_one_feedback() -> None:
    reports = [
        _report("insight_mock_001", "第一份报告解释"),
        _report("insight_mock_001", "第二份报告解释"),
    ]
    feedback = [_feedback("feedback_negative", "insight_mock_001", "not_me")]

    profile = build_profile_from_sources("user_001", reports, feedback)

    assert profile.profile is not None
    feedback_evidence = [
        evidence
        for item in profile.profile.items
        for evidence in item.evidence
        if evidence.evidence_id == "feedback_negative"
    ]
    assert len(feedback_evidence) == 1
    assert feedback_evidence[0].direction == "negative"


def _report(insight_id: str, title: str) -> ReportResponse:
    return ReportResponse(
        reportId=f"report_{insight_id}",
        title="测试报告",
        summary="测试报告摘要",
        lowLevelFeatures=[],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[
            Insight(
                insightId=insight_id,
                title=title,
                observation="观察到一组可追溯审美信号。",
                evidenceRefs=["input_001"],
                interpretation="这是一条可被用户反馈修正的解释。",
                uncertainty="需要用户反馈确认。",
                confidence=0.5,
            )
        ],
        disclaimer="测试报告不是人格诊断。",
    )


def _feedback(feedback_id: str, insight_id: str, rating: str) -> InsightFeedbackResponse:
    return InsightFeedbackResponse(
        id=feedback_id,
        userId="user_001",
        insightId=insight_id,
        interpretationId=None,
        rating=rating,
        comment=None,
        createdAt=utc_now() + timedelta(seconds=len(feedback_id)),
    )

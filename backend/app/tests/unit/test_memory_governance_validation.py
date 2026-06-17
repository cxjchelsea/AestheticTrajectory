from datetime import timedelta

from app.schemas.common import utc_now
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.report import Insight, ReportResponse
from app.services.profile_builder import build_profile_from_sources


DIAGNOSTIC_TERMS = ("人格", "心理", "能力", "命运", "灵魂", "你一定")


def test_v2e_profile_items_are_evidence_backed_and_non_diagnostic() -> None:
    reports = [_report_with_feature("report_001", "input_001", "low")]

    profile = build_profile_from_sources("user_001", reports, [])

    assert profile.profile is not None
    assert profile.profile.items
    assert all(item.evidence for item in profile.profile.items)
    assert all(item.source_count == len(item.evidence) for item in profile.profile.items)
    assert not _contains_diagnostic_terms(profile.profile.summary)
    assert all(not _contains_diagnostic_terms(evidence.note) for item in profile.profile.items for evidence in item.evidence)


def test_v2e_rejected_interpretation_does_not_recur_as_positive_profile_item() -> None:
    reports = [
        _report_with_insight("report_001", "insight_001", "工业化孤独感"),
        _report_with_insight("report_002", "insight_002", "工业化孤独感"),
    ]
    feedback = [_feedback("feedback_negative", "insight_001", "not_me", "这个解释不像我")]

    profile = build_profile_from_sources("user_001", reports, feedback)

    assert profile.profile is not None
    rejected_items = [item for item in profile.profile.items if item.status == "rejected"]
    positive_labels = {
        item.label
        for item in profile.profile.items
        if item.status in {"stable", "recent"} and item.weight > 0
    }

    assert rejected_items
    assert rejected_items[0].label == "工业化孤独感"
    assert rejected_items[0].evidence[0].direction == "negative"
    assert "工业化孤独感" not in positive_labels
    assert "工业化孤独感" not in profile.profile.summary


def test_v2e_uncertain_feedback_remains_visible_but_does_not_strengthen_summary() -> None:
    report = _report_with_insight("report_001", "insight_001", "复古怀旧感")
    feedback = [_feedback("feedback_unsure", "insight_001", "unsure", "还不能确定")]

    profile = build_profile_from_sources("user_001", [report], feedback)

    assert profile.profile is not None
    item = profile.profile.items[0]
    assert item.status == "uncertain"
    assert item.weight == 0
    assert item.evidence[0].direction == "uncertain"
    assert "复古怀旧感" not in profile.profile.summary


def test_v2e_feedback_update_snapshot_uses_latest_feedback_only() -> None:
    report = _report_with_insight("report_001", "insight_001", "冷感空间偏好")
    latest_feedback = _feedback("feedback_latest", "insight_001", "not_me", "更新后不像我")

    profile = build_profile_from_sources("user_001", [report], [latest_feedback])

    assert profile.profile is not None
    item = profile.profile.items[0]
    assert item.status == "rejected"
    assert item.weight < 0
    assert [evidence.evidence_id for evidence in item.evidence] == ["feedback_latest"]
    assert item.evidence[0].direction == "negative"
    assert "冷感空间偏好" not in profile.profile.summary


def _report_with_feature(report_id: str, input_id: str, density: str) -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title="测试报告",
        summary="测试报告摘要",
        lowLevelFeatures=[
            InputFeature(
                inputId=input_id,
                featureType="text",
                lowLevelFeatures={
                    "density": FeatureSignal(
                        value=density,
                        confidence=0.8,
                        evidence=["样本呈现低密度视觉结构"],
                    )
                },
                sampleEvidence=["可追溯样本证据"],
                promptVersion="test",
                modelName="mock",
            )
        ],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[],
        disclaimer="测试报告。",
    )


def _report_with_insight(report_id: str, insight_id: str, title: str) -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
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
        disclaimer="测试报告。",
    )


def _feedback(feedback_id: str, insight_id: str, rating: str, comment: str) -> InsightFeedbackResponse:
    return InsightFeedbackResponse(
        id=feedback_id,
        userId="user_001",
        insightId=insight_id,
        interpretationId=None,
        rating=rating,
        comment=comment,
        createdAt=utc_now() + timedelta(seconds=len(feedback_id)),
    )


def _contains_diagnostic_terms(text: str) -> bool:
    return any(term in text for term in DIAGNOSTIC_TERMS)

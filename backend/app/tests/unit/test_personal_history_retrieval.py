from app.schemas.common import utc_now
from app.schemas.feature import InputFeature
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.history_context import PersonalHistoryContext
from app.schemas.report import ReportResponse
from app.services.personal_history_retrieval import build_personal_history_context


def test_personal_history_context_returns_empty_state_without_prior_reports() -> None:
    context = build_personal_history_context(
        "report_current",
        _features("warm"),
        [],
        [],
    )

    assert context.items == []
    assert context.message == "暂无可参考的历史报告。"


def test_personal_history_context_matches_feature_overlap_and_feedback_signals() -> None:
    previous = _report("report_previous", "warm", insight_id="report_previous_insight")
    current_features = _features("warm")
    feedback = [
        InsightFeedbackResponse(
            id="feedback_positive",
            userId="user_a",
            insightId="report_previous_insight",
            interpretationId=None,
            rating="very_me",
            comment="认可",
            createdAt=utc_now(),
        )
    ]

    context = build_personal_history_context(
        "report_current",
        current_features,
        [previous],
        feedback,
    )

    assert context.items
    assert any(item.source_type == "report" for item in context.items)
    assert any(item.direction == "positive" for item in context.items)
    assert all(item.source_refs for item in context.items)
    assert context.summary is not None
    assert "人格" not in (context.summary or "")


def test_personal_history_context_excludes_not_me_from_positive_direction() -> None:
    previous = _report("report_previous", "warm", insight_id="report_previous_insight")
    feedback = [
        InsightFeedbackResponse(
            id="feedback_negative",
            userId="user_a",
            insightId="report_previous_insight",
            interpretationId=None,
            rating="not_me",
            comment="否定",
            createdAt=utc_now(),
        )
    ]

    context = build_personal_history_context(
        "report_current",
        _features("warm"),
        [previous],
        feedback,
    )

    assert any(item.direction == "negative" for item in context.items)
    assert not any(item.direction == "positive" for item in context.items)


def _features(mood_value: str) -> list[InputFeature]:
    return [
        InputFeature(
            inputId="input_1",
            featureType="text",
            lowLevelFeatures={
                "color_mood": {
                    "value": mood_value,
                    "confidence": 0.8,
                    "evidence": ["evidence_1"],
                }
            },
            sampleEvidence=["sample evidence"],
            promptVersion="test",
            modelName="mock",
        )
    ]


def _report(report_id: str, mood_value: str, insight_id: str = "insight_1") -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title=f"{report_id} title",
        summary=f"{report_id} summary",
        lowLevelFeatures=_features(mood_value),
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[
            {
                "insightId": insight_id,
                "title": "柔和秩序",
                "observation": "观察到局部结构。",
                "evidenceRefs": ["input_1"],
                "interpretation": "结构差异。",
                "uncertainty": "测试。",
                "confidence": 0.7,
            }
        ],
        disclaimer="测试免责声明。",
    )

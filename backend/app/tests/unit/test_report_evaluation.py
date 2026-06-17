from app.schemas.common import utc_now
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.report import ReportResponse
from app.services.schema_validation_summary import build_schema_validation_records
from app.services.report_evaluation import build_report_evaluation


def test_report_evaluation_metrics_cover_evidence_and_retrieval() -> None:
    report = _report()
    evaluation = build_report_evaluation(report, [], build_schema_validation_records([]))

    assert evaluation.metrics.evidence_coverage == 1.0
    assert evaluation.metrics.retrieval_coverage == 1.0
    assert evaluation.metrics.unsupported_insight_count == 0
    assert evaluation.metrics.feedback_hit_rate is None
    assert evaluation.metrics.knowledge_context_item_count == 1
    assert "人格" not in evaluation.summary


def test_report_evaluation_counts_unsupported_insights() -> None:
    report = ReportResponse(
        reportId="report_bad",
        title="title",
        summary="summary",
        lowLevelFeatures=[
            {
                "inputId": "input_1",
                "featureType": "text",
                "lowLevelFeatures": {
                    "saturation": {"value": "low", "confidence": 0.8, "evidence": ["evidence_1"]},
                },
                "sampleEvidence": ["sample"],
                "promptVersion": "test",
                "modelName": "mock",
            }
        ],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[
            {
                "insightId": "insight_bad",
                "title": "无证据洞察",
                "observation": "没有绑定当前输入。",
                "evidenceRefs": ["missing_input"],
                "interpretation": "测试",
                "uncertainty": "测试",
                "confidence": 0.5,
            }
        ],
        disclaimer="测试",
    )

    evaluation = build_report_evaluation(report, [], [])

    assert evaluation.metrics.unsupported_insight_count == 1
    assert evaluation.metrics.evidence_coverage == 1.0


def test_report_evaluation_feedback_hit_rate() -> None:
    report = _report()
    feedback = [
        InsightFeedbackResponse(
            id="feedback_1",
            userId="user_a",
            insightId="report_insight",
            interpretationId=None,
            rating="very_me",
            comment="认可",
            createdAt=utc_now(),
        ),
        InsightFeedbackResponse(
            id="feedback_2",
            userId="user_a",
            insightId="other_insight",
            interpretationId=None,
            rating="not_me",
            comment="否定",
            createdAt=utc_now(),
        ),
    ]

    evaluation = build_report_evaluation(report, feedback, [])

    assert evaluation.metrics.feedback_hit_rate == 1.0


def _report() -> ReportResponse:
    return ReportResponse(
        reportId="report_001",
        title="title",
        summary="summary",
        lowLevelFeatures=[
            {
                "inputId": "input_1",
                "featureType": "text",
                "lowLevelFeatures": {
                    "saturation": {"value": "low", "confidence": 0.8, "evidence": ["evidence_1"]},
                },
                "sampleEvidence": ["sample"],
                "promptVersion": "test",
                "modelName": "mock",
            }
        ],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[
            {
                "insightId": "report_insight",
                "title": "柔和秩序",
                "observation": "观察到结构。",
                "evidenceRefs": ["input_1"],
                "interpretation": "解释",
                "uncertainty": "测试",
                "confidence": 0.7,
            }
        ],
        disclaimer="测试",
        knowledgeContext={
            "items": [
                {
                    "docId": "kb_1",
                    "title": "低饱和",
                    "snippet": "snippet",
                    "matchedFeatures": ["saturation=low"],
                    "sourceRefs": ["kb_1", "project-aesthetic-knowledge-v1"],
                    "note": "note",
                }
            ],
            "summary": "summary",
            "disclaimer": "disclaimer",
        },
    )

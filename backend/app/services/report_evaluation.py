from app.schemas.analysis_debug import SchemaValidationRecord
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.report import ReportResponse
from app.schemas.report_evaluation import ReportEvaluationMetrics, ReportEvaluationResponse

DISCLAIMER = "这些指标用于开发期质量观察，不代表对用户的人格、心理或能力判断。"

POSITIVE_FEEDBACK = {"somewhat_me", "very_me"}


def build_report_evaluation(
    report: ReportResponse,
    feedback: list[InsightFeedbackResponse],
    schema_validation: list[SchemaValidationRecord] | None = None,
) -> ReportEvaluationResponse:
    input_ids = {feature.input_id for feature in report.low_level_features}
    insight_ids = {insight.insight_id for insight in report.insights}
    report_feedback = [item for item in feedback if item.insight_id in insight_ids]

    metrics = ReportEvaluationMetrics(
        evidenceCoverage=_evidence_coverage(report, input_ids),
        retrievalCoverage=_retrieval_coverage(report),
        unsupportedInsightCount=_unsupported_insight_count(report, input_ids),
        feedbackHitRate=_feedback_hit_rate(report_feedback),
        schemaPassRate=_schema_pass_rate(schema_validation or []),
        insightCount=len(report.insights),
        historyContextItemCount=_history_item_count(report),
        knowledgeContextItemCount=_knowledge_item_count(report),
    )

    return ReportEvaluationResponse(
        reportId=report.report_id,
        metrics=metrics,
        summary=_summary(metrics),
        disclaimer=DISCLAIMER,
    )


def _evidence_coverage(report: ReportResponse, input_ids: set[str]) -> float:
    if not report.insights:
        return 1.0
    grounded = sum(
        1
        for insight in report.insights
        if insight.evidence_refs and any(ref in input_ids for ref in insight.evidence_refs)
    )
    return grounded / len(report.insights)


def _unsupported_insight_count(report: ReportResponse, input_ids: set[str]) -> int:
    unsupported = 0
    for insight in report.insights:
        if not insight.evidence_refs:
            unsupported += 1
            continue
        if not any(ref in input_ids for ref in insight.evidence_refs):
            unsupported += 1
    return unsupported


def _retrieval_coverage(report: ReportResponse) -> float:
    items = _retrieval_items(report)
    if not items:
        return 1.0
    with_refs = sum(1 for item in items if item.source_refs)
    return with_refs / len(items)


def _retrieval_items(report: ReportResponse) -> list:
    items = []
    if report.history_context is not None:
        items.extend(report.history_context.items)
    if report.knowledge_context is not None:
        items.extend(report.knowledge_context.items)
    return items


def _history_item_count(report: ReportResponse) -> int:
    if report.history_context is None:
        return 0
    return len(report.history_context.items)


def _knowledge_item_count(report: ReportResponse) -> int:
    if report.knowledge_context is None:
        return 0
    return len(report.knowledge_context.items)


def _feedback_hit_rate(feedback: list[InsightFeedbackResponse]) -> float | None:
    if not feedback:
        return None
    positive = sum(1 for item in feedback if item.rating in POSITIVE_FEEDBACK)
    return positive / len(feedback)


def _schema_pass_rate(schema_validation: list[SchemaValidationRecord]) -> float | None:
    applicable = [
        record for record in schema_validation if record.status in {"passed", "failed"}
    ]
    if not applicable:
        return None
    passed = sum(1 for record in applicable if record.status == "passed")
    return passed / len(applicable)


def _summary(metrics: ReportEvaluationMetrics) -> str:
    feedback_text = (
        f"feedback hit rate {metrics.feedback_hit_rate:.0%}。"
        if metrics.feedback_hit_rate is not None
        else "尚无用户反馈。"
    )
    return (
        f"当前报告 evidence coverage {metrics.evidence_coverage:.0%}，"
        f"retrieval coverage {metrics.retrieval_coverage:.0%}，"
        f"unsupported insight {metrics.unsupported_insight_count} 条，"
        f"schema pass rate {_format_rate(metrics.schema_pass_rate)}；{feedback_text}"
    )


def _format_rate(value: float | None) -> str:
    if value is None:
        return "暂无 workflow schema 记录"
    return f"{value:.0%}"

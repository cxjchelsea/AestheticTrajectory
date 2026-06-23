from types import SimpleNamespace

from app.schemas.history_context import HistoryContextItem, PersonalHistoryContext
from app.schemas.knowledge_context import AestheticKnowledgeContext, KnowledgeContextItem, KnowledgeRetrievalMeta
from app.schemas.report import Insight, ReportResponse
from app.schemas.report_evaluation import ReportEvaluationMetrics
from app.services.observability_trace import build_debug_traces


def _report(
    *,
    history: PersonalHistoryContext | None = None,
    knowledge: AestheticKnowledgeContext | None = None,
    metrics: ReportEvaluationMetrics | None = None,
) -> ReportResponse:
    return ReportResponse(
        reportId="report_test",
        title="test",
        summary="summary",
        lowLevelFeatures=[],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[
            Insight(
                insightId="insight_1",
                title="insight",
                observation="obs",
                evidenceRefs=["input_1"],
                interpretation="interp",
                uncertainty="low",
                confidence=0.8,
            )
        ],
        disclaimer="disclaimer",
        historyContext=history,
        knowledgeContext=knowledge,
        evaluationMetrics=metrics,
    )


def _success_log(step_id: str):
    return SimpleNamespace(step_id=step_id, status="success", latency_ms=12)


def test_debug_traces_mark_history_abstention() -> None:
    report = _report(
        history=PersonalHistoryContext(message="暂无可参考的历史报告。", disclaimer="d"),
        knowledge=AestheticKnowledgeContext(
            items=[
                KnowledgeContextItem(
                    docId="doc_1",
                    title="Low saturation",
                    snippet="snippet",
                    matchedFeatures=["saturation=low"],
                    sourceRefs=["doc_1", "kb"],
                    note="note",
                )
            ],
            disclaimer="d",
        ),
    )
    logs = [
        _success_log("retrieve_personal_history"),
        _success_log("retrieve_aesthetic_knowledge"),
        _success_log("compute_report_evaluation"),
    ]

    retrieval_trace, retrieval_items, context_trace, evaluation_trace = build_debug_traces(
        report,
        logs,
        [],
    )

    history_trace = next(item for item in retrieval_trace if item.retrieval_type == "personal_history")
    assert history_trace.abstained is True
    assert history_trace.selected_item_count == 0
    assert context_trace is not None
    assert context_trace.history_abstained is True
    assert context_trace.knowledge_item_count == 1
    assert len(retrieval_items) == 1
    assert retrieval_items[0].retrieval_type == "aesthetic_knowledge"
    assert evaluation_trace is None


def test_debug_traces_include_history_items_and_evaluation() -> None:
    metrics = ReportEvaluationMetrics(
        evidenceCoverage=1.0,
        retrievalCoverage=1.0,
        unsupportedInsightCount=0,
        feedbackHitRate=None,
        schemaPassRate=1.0,
        insightCount=1,
        historyContextItemCount=1,
        knowledgeContextItemCount=1,
    )
    report = _report(
        history=PersonalHistoryContext(
            items=[
                HistoryContextItem(
                    sourceType="report",
                    sourceId="report_prev",
                    sourceRefs=["report_prev"],
                    direction="neutral",
                    matchedFeatures=["density=high"],
                    label="Previous report",
                    note="overlap",
                )
            ],
            disclaimer="d",
        ),
        knowledge=AestheticKnowledgeContext(
            items=[
                KnowledgeContextItem(
                    docId="doc_1",
                    title="Density",
                    snippet="snippet",
                    matchedFeatures=["density=high"],
                    sourceRefs=["doc_1"],
                    note="note",
                )
            ],
            disclaimer="d",
        ),
        metrics=metrics,
    )
    logs = [
        _success_log("retrieve_personal_history"),
        _success_log("retrieve_aesthetic_knowledge"),
        _success_log("compute_report_evaluation"),
    ]

    retrieval_trace, retrieval_items, context_trace, evaluation_trace = build_debug_traces(
        report,
        logs,
        [],
    )

    assert all(not step.abstained for step in retrieval_trace)
    assert len(retrieval_items) == 2
    assert context_trace is not None
    assert context_trace.total_selected_items == 2
    assert evaluation_trace is not None
    assert evaluation_trace.metrics.evidence_coverage == 1.0
    assert evaluation_trace.step_status == "success"


def test_debug_traces_mark_knowledge_vector_degradation() -> None:
    report = _report(
        knowledge=AestheticKnowledgeContext(
            items=[
                KnowledgeContextItem(
                    docId="doc_1",
                    title="Low saturation",
                    snippet="snippet",
                    matchedFeatures=["saturation=low"],
                    sourceRefs=["doc_1"],
                    note="note",
                )
            ],
            disclaimer="d",
            retrievalMeta=KnowledgeRetrievalMeta(
                tagMatchCount=1,
                graphHitCount=0,
                vectorPath="failed",
                vectorErrorMessage="chroma unavailable",
            ),
        )
    )
    logs = [_success_log("retrieve_aesthetic_knowledge")]

    retrieval_trace, _, _, _ = build_debug_traces(report, logs, [])

    knowledge_trace = next(item for item in retrieval_trace if item.retrieval_type == "aesthetic_knowledge")
    assert knowledge_trace.status == "degraded"
    assert knowledge_trace.vector_path == "failed"
    assert "degraded" in knowledge_trace.developer_message

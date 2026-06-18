from app.repositories.memory_store import MemoryStore
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import utc_now
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.history_context import HistoryContextItem, PersonalHistoryContext
from app.schemas.input import AestheticInputResponse
from app.schemas.knowledge_context import AestheticKnowledgeContext, KnowledgeContextItem
from app.schemas.report import Insight, ReportResponse
from app.services.profile_builder import build_profile_from_sources
from app.services.report_evaluation import build_report_evaluation
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence, run_mock_aesthetic_analysis


DIAGNOSTIC_TERMS = ("人格", "心理", "能力", "命运", "灵魂", "你一定", "消费规训")


def test_v3e_workflow_insights_only_reference_current_inputs() -> None:
    store = MemoryStore()
    report = _run_workflow(store, job_id="job_v3e_1", input_count=3)

    input_ids = {feature.input_id for feature in report.low_level_features}
    assert report.insights
    for insight in report.insights:
        assert insight.evidence_refs
        assert all(ref in input_ids for ref in insight.evidence_refs)


def test_v3e_second_workflow_run_keeps_history_separate_from_insight_evidence() -> None:
    store = MemoryStore()
    first_report = _run_workflow(store, job_id="job_v3e_first", input_count=3)
    second_report = _run_workflow(store, job_id="job_v3e_second", input_count=3, input_prefix="followup")

    assert second_report.history_context is not None
    assert second_report.history_context.items
    assert any(item.source_type == "report" for item in second_report.history_context.items)

    second_input_ids = {feature.input_id for feature in second_report.low_level_features}
    history_source_ids = {
        item.source_id
        for item in second_report.history_context.items
        if item.source_type == "report"
    }
    assert first_report.report_id in history_source_ids

    for insight in second_report.insights:
        assert all(ref in second_input_ids for ref in insight.evidence_refs)
        assert all(ref not in history_source_ids for ref in insight.evidence_refs)


def test_v3e_knowledge_and_history_context_do_not_feed_profile_positive_evidence() -> None:
    reports = [
        _report_with_contexts(
            report_id="report_knowledge",
            input_id="input_001",
            knowledge_doc_id="kb_low_saturation",
        )
    ]
    feedback = [
        InsightFeedbackResponse(
            id="feedback_positive",
            userId="user_001",
            insightId="insight_001",
            interpretationId=None,
            rating="very_me",
            comment="认可",
            createdAt=utc_now(),
        )
    ]

    profile = build_profile_from_sources("user_001", reports, feedback)

    assert profile.profile is not None
    positive_evidence_ids = {
        evidence.evidence_id
        for item in profile.profile.items
        if item.status in {"stable", "recent"} and item.weight > 0
        for evidence in item.evidence
    }
    assert "kb_low_saturation" not in positive_evidence_ids
    assert all(not evidence.evidence_id.startswith("kb_") for item in profile.profile.items for evidence in item.evidence)
    assert all(not evidence.note.startswith("知识库") for item in profile.profile.items for evidence in item.evidence)


def test_v3e_not_me_history_feedback_stays_negative_context() -> None:
    history = PersonalHistoryContext(
        items=[
            HistoryContextItem(
                sourceType="feedback",
                sourceId="feedback_negative",
                sourceRefs=["report_prev", "insight_prev"],
                direction="negative",
                matchedFeatures=["density=low"],
                label="冷感空间",
                note="用户曾否定这一解释方向。",
            )
        ],
        disclaimer="历史参考 disclaimer。",
    )

    assert all(item.direction != "positive" or item.source_type != "feedback" for item in history.items)
    assert history.items[0].direction == "negative"


def test_v3e_workflow_evaluation_reports_no_unsupported_insights() -> None:
    store = MemoryStore()
    report = _run_workflow(store, job_id="job_v3e_eval", input_count=3)

    evaluation = build_report_evaluation(report, [])
    assert evaluation.metrics.unsupported_insight_count == 0
    assert evaluation.metrics.evidence_coverage == 1.0
    assert report.evaluation_metrics is not None
    assert report.evaluation_metrics.unsupported_insight_count == 0


def test_v3e_context_and_evaluation_copy_are_non_diagnostic() -> None:
    store = MemoryStore()
    report = _run_workflow(store, job_id="job_v3e_copy", input_count=3)

    texts: list[str] = []
    if report.history_context is not None:
        texts.extend([report.history_context.message or "", report.history_context.summary or ""])
        texts.extend(item.note for item in report.history_context.items)
    if report.knowledge_context is not None:
        texts.extend([report.knowledge_context.message or "", report.knowledge_context.summary or ""])
        texts.extend(item.note for item in report.knowledge_context.items)

    assert all(not _contains_diagnostic_terms(text) for text in texts if text)


def _run_workflow(
    store: MemoryStore,
    *,
    job_id: str,
    input_count: int,
    input_prefix: str = "sample",
) -> ReportResponse:
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id=f"{job_id}_input_{index}",
            userId="user_anonymous",
            type="text",
            contentText=f"{input_prefix} {index}",
            fileUrl=None,
            source="test",
            title=f"{input_prefix} {index}",
            description=None,
            createdAt=now,
        )
        for index in range(input_count)
    ]
    job = AnalysisJobResponse(
        id=job_id,
        userId="user_anonymous",
        status="created",
        inputCount=input_count,
        errorMessage=None,
        reportId=None,
        createdAt=now,
        startedAt=now,
        finishedAt=None,
    )

    result = run_mock_aesthetic_analysis(job, inputs, memory_workflow_persistence(store))
    assert result.status == "completed"
    assert result.report_id is not None
    return store.reports[result.report_id]


def _report_with_contexts(
    *,
    report_id: str,
    input_id: str,
    knowledge_doc_id: str,
) -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title="测试报告",
        summary="测试报告摘要",
        lowLevelFeatures=[],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[
            Insight(
                insightId="insight_001",
                title="低饱和冷感",
                observation="观察到低饱和结构。",
                evidenceRefs=[input_id],
                interpretation="可能呈现冷感审美。",
                uncertainty="需要更多样本确认。",
                confidence=0.7,
            )
        ],
        disclaimer="测试报告。",
        historyContext=PersonalHistoryContext(
            items=[
                HistoryContextItem(
                    sourceType="report",
                    sourceId="report_prev",
                    sourceRefs=["report_prev"],
                    direction="neutral",
                    matchedFeatures=["saturation=low"],
                    label="历史报告",
                    note="历史结构参考。",
                )
            ],
            disclaimer="历史参考不是人格判断。",
        ),
        knowledgeContext=AestheticKnowledgeContext(
            items=[
                KnowledgeContextItem(
                    docId=knowledge_doc_id,
                    title="低饱和审美",
                    snippet="知识库解释片段。",
                    matchedFeatures=["saturation=low"],
                    sourceRefs=[knowledge_doc_id, "aesthetic_kb"],
                    note="知识库条目用于解释风格概念。",
                )
            ],
            disclaimer="知识参考不代表用户偏好证据。",
        ),
    )


def _contains_diagnostic_terms(text: str) -> bool:
    return any(term in text for term in DIAGNOSTIC_TERMS)

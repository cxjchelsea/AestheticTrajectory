from app.schemas.analysis_debug import (
    ContextAssemblyTrace,
    EvaluationTrace,
    RetrievalItemTrace,
    RetrievalStepTrace,
    SchemaValidationRecord,
)
from app.schemas.report import ReportResponse


RETRIEVAL_STEPS = (
    ("retrieve_personal_history", "personal_history"),
    ("retrieve_aesthetic_knowledge", "aesthetic_knowledge"),
)


def build_debug_traces(
    report: ReportResponse | None,
    logs,
    schema_validation: list[SchemaValidationRecord],
) -> tuple[
    list[RetrievalStepTrace],
    list[RetrievalItemTrace],
    ContextAssemblyTrace | None,
    EvaluationTrace | None,
]:
    if report is None:
        return [], [], None, None

    logs_by_step = {log.step_id: log for log in logs}
    retrieval_trace = _build_retrieval_step_traces(report, logs_by_step)
    retrieval_items = _build_retrieval_item_traces(report)
    context_assembly_trace = _build_context_assembly_trace(report)
    evaluation_trace = _build_evaluation_trace(report, logs_by_step, schema_validation)
    return retrieval_trace, retrieval_items, context_assembly_trace, evaluation_trace


def _build_retrieval_step_traces(report: ReportResponse, logs_by_step) -> list[RetrievalStepTrace]:
    traces: list[RetrievalStepTrace] = []
    for step_id, retrieval_type in RETRIEVAL_STEPS:
        log = logs_by_step.get(step_id)
        graph_hit_count = None
        vector_path = None
        tag_match_count = None
        if retrieval_type == "personal_history":
            context = report.history_context
            selected_count = len(context.items) if context is not None else 0
            abstained = selected_count == 0
            message = context.message if context is not None else None
            developer_message = (
                "Personal history retrieval abstained; no sufficiently relevant history items were selected."
                if abstained
                else f"Personal history retrieval selected {selected_count} item(s) with feature overlap."
            )
        else:
            context = report.knowledge_context
            selected_count = len(context.items) if context is not None else 0
            abstained = selected_count == 0
            message = context.message if context is not None else None
            meta = context.retrieval_meta if context is not None else None
            graph_hit_count = meta.graph_hit_count if meta is not None else None
            vector_path = meta.vector_path if meta is not None else None
            tag_match_count = meta.tag_match_count if meta is not None else None
            if abstained:
                reason = meta.abstention_reason if meta is not None else "no_tag_overlap"
                developer_message = (
                    f"Aesthetic knowledge retrieval abstained ({reason}); "
                    "no knowledge chunk met the minimum feature overlap."
                )
            else:
                graph_part = f" graph hits={graph_hit_count or 0}" if graph_hit_count is not None else ""
                vector_part = f" vector={vector_path}" if vector_path else ""
                developer_message = (
                    f"Aesthetic knowledge retrieval selected {selected_count} chunk(s) for explanation support;"
                    f"{graph_part}{vector_part}."
                )

        traces.append(
            RetrievalStepTrace(
                stepId=step_id,
                retrievalType=retrieval_type,
                status=log.status if log is not None else "not_recorded",
                latencyMs=log.latency_ms if log is not None else None,
                selectedItemCount=selected_count,
                abstained=abstained,
                message=message,
                developerMessage=developer_message,
                graphHitCount=graph_hit_count if retrieval_type == "aesthetic_knowledge" else None,
                vectorPath=vector_path if retrieval_type == "aesthetic_knowledge" else None,
                tagMatchCount=tag_match_count if retrieval_type == "aesthetic_knowledge" else None,
            )
        )
    return traces


def _build_retrieval_item_traces(report: ReportResponse) -> list[RetrievalItemTrace]:
    items: list[RetrievalItemTrace] = []

    if report.history_context is not None:
        for item in report.history_context.items:
            items.append(
                RetrievalItemTrace(
                    retrievalType="personal_history",
                    itemId=item.source_id,
                    label=item.label,
                    matchedFeatures=item.matched_features,
                    sourceRefs=item.source_refs,
                    direction=item.direction,
                    note=item.note,
                )
            )

    if report.knowledge_context is not None:
        for item in report.knowledge_context.items:
            items.append(
                RetrievalItemTrace(
                    retrievalType="aesthetic_knowledge",
                    itemId=item.doc_id,
                    label=item.title,
                    matchedFeatures=item.matched_features,
                    sourceRefs=item.source_refs,
                    direction=None,
                    note=item.note,
                )
            )

    return items


def _build_context_assembly_trace(report: ReportResponse) -> ContextAssemblyTrace:
    history_count = len(report.history_context.items) if report.history_context is not None else 0
    knowledge_count = len(report.knowledge_context.items) if report.knowledge_context is not None else 0
    history_abstained = history_count == 0
    knowledge_abstained = knowledge_count == 0
    history_message = report.history_context.message if report.history_context is not None else None
    knowledge_message = report.knowledge_context.message if report.knowledge_context is not None else None

    if history_abstained and knowledge_abstained:
        developer_message = (
            "Context assembly produced no history or knowledge items; report generation relied on current input only."
        )
    elif history_abstained:
        developer_message = (
            f"Context assembly attached {knowledge_count} knowledge item(s); history retrieval abstained."
        )
    elif knowledge_abstained:
        developer_message = (
            f"Context assembly attached {history_count} history item(s); knowledge retrieval abstained."
        )
    else:
        developer_message = (
            f"Context assembly attached {history_count} history item(s) and {knowledge_count} knowledge item(s)."
        )

    return ContextAssemblyTrace(
        historyItemCount=history_count,
        knowledgeItemCount=knowledge_count,
        totalSelectedItems=history_count + knowledge_count,
        historyAbstained=history_abstained,
        knowledgeAbstained=knowledge_abstained,
        historyMessage=history_message,
        knowledgeMessage=knowledge_message,
        developerMessage=developer_message,
    )


def _build_evaluation_trace(
    report: ReportResponse,
    logs_by_step,
    schema_validation: list[SchemaValidationRecord],
) -> EvaluationTrace | None:
    if report.evaluation_metrics is None:
        return None

    log = logs_by_step.get("compute_report_evaluation")
    applicable = [record for record in schema_validation if record.status in {"passed", "failed"}]
    passed = sum(1 for record in applicable if record.status == "passed")
    schema_pass_rate = passed / len(applicable) if applicable else None

    return EvaluationTrace(
        stepId="compute_report_evaluation",
        stepStatus=log.status if log is not None else "not_recorded",
        latencyMs=log.latency_ms if log is not None else None,
        metrics=report.evaluation_metrics,
        schemaPassRate=schema_pass_rate,
        schemaRecordCount=len(schema_validation),
        developerMessage=(
            "Evaluation metrics were computed from persisted report facts and workflow schema validation records."
        ),
    )

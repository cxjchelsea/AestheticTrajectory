from app.schemas.analysis_debug import SchemaValidationRecord


def build_schema_validation_records(logs) -> list[SchemaValidationRecord]:
    logs_by_step = {log.step_id: log for log in logs}
    schema_steps = [
        ("extract_features", "InputFeature"),
        ("generate_embeddings", "EmbeddingRecord"),
        ("cluster_inputs", "SimilarityGroup / PossibleInterpretation / Insight"),
        ("retrieve_personal_history", "PersonalHistoryContext"),
        ("retrieve_aesthetic_knowledge", "AestheticKnowledgeContext"),
        ("generate_report", "ReportResponse"),
        ("compute_report_evaluation", "ReportEvaluationMetrics"),
        ("save_report", "PersistenceWrite"),
    ]
    records: list[SchemaValidationRecord] = []
    for step_id, schema_name in schema_steps:
        log = logs_by_step.get(step_id)
        if log is None:
            status = "not_recorded"
            message = "No workflow log was recorded for this schema boundary."
        elif log.status == "success":
            status = "passed"
            message = "Workflow step completed and produced data accepted by the current schema boundary."
        else:
            status = "failed"
            message = log.error_message or "Workflow step failed before schema output was accepted."
        records.append(
            SchemaValidationRecord(
                stepId=step_id,
                schemaName=schema_name,
                status=status,
                developerMessage=message,
            )
        )
    return records

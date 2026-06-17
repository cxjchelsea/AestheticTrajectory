from pydantic import BaseModel, Field


class ReportEvaluationMetrics(BaseModel):
    evidence_coverage: float = Field(alias="evidenceCoverage")
    retrieval_coverage: float = Field(alias="retrievalCoverage")
    unsupported_insight_count: int = Field(alias="unsupportedInsightCount")
    feedback_hit_rate: float | None = Field(default=None, alias="feedbackHitRate")
    schema_pass_rate: float | None = Field(default=None, alias="schemaPassRate")
    insight_count: int = Field(alias="insightCount")
    history_context_item_count: int = Field(alias="historyContextItemCount")
    knowledge_context_item_count: int = Field(alias="knowledgeContextItemCount")

    model_config = {"populate_by_name": True}


class ReportEvaluationResponse(BaseModel):
    report_id: str = Field(alias="reportId")
    metrics: ReportEvaluationMetrics
    summary: str
    disclaimer: str

    model_config = {"populate_by_name": True}

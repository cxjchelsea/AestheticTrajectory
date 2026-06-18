from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.report_evaluation import ReportEvaluationMetrics


FallbackSeverity = Literal["info", "warning", "error"]
MockUsageStatus = Literal["enabled", "disabled"]
SchemaValidationStatus = Literal["passed", "failed", "not_recorded"]
BoundaryWarningStatus = Literal["not_used", "planned", "dev_only"]


class FallbackEvent(BaseModel):
    id: str
    job_id: str = Field(alias="jobId")
    step_id: str = Field(alias="stepId")
    fallback_type: str = Field(alias="fallbackType")
    original_error: str = Field(alias="originalError")
    fallback_action: str = Field(alias="fallbackAction")
    severity: FallbackSeverity
    user_visible: bool = Field(alias="userVisible")
    developer_message: str = Field(alias="developerMessage")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class MockUsageRecord(BaseModel):
    component: str
    status: MockUsageStatus
    dev_only: bool = Field(alias="devOnly")
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


class SchemaValidationRecord(BaseModel):
    step_id: str = Field(alias="stepId")
    schema_name: str = Field(alias="schemaName")
    status: SchemaValidationStatus
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


class BoundaryWarning(BaseModel):
    capability: str
    status: BoundaryWarningStatus
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


RetrievalType = Literal["personal_history", "aesthetic_knowledge"]


class RetrievalStepTrace(BaseModel):
    step_id: str = Field(alias="stepId")
    retrieval_type: RetrievalType = Field(alias="retrievalType")
    status: str
    latency_ms: int | None = Field(default=None, alias="latencyMs")
    selected_item_count: int = Field(alias="selectedItemCount")
    abstained: bool
    message: str | None = None
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


class RetrievalItemTrace(BaseModel):
    retrieval_type: RetrievalType = Field(alias="retrievalType")
    item_id: str = Field(alias="itemId")
    label: str
    matched_features: list[str] = Field(alias="matchedFeatures")
    source_refs: list[str] = Field(alias="sourceRefs")
    direction: str | None = None
    note: str

    model_config = {"populate_by_name": True}


class ContextAssemblyTrace(BaseModel):
    history_item_count: int = Field(alias="historyItemCount")
    knowledge_item_count: int = Field(alias="knowledgeItemCount")
    total_selected_items: int = Field(alias="totalSelectedItems")
    history_abstained: bool = Field(alias="historyAbstained")
    knowledge_abstained: bool = Field(alias="knowledgeAbstained")
    history_message: str | None = Field(default=None, alias="historyMessage")
    knowledge_message: str | None = Field(default=None, alias="knowledgeMessage")
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


class EvaluationTrace(BaseModel):
    step_id: str = Field(alias="stepId")
    step_status: str = Field(alias="stepStatus")
    latency_ms: int | None = Field(default=None, alias="latencyMs")
    metrics: ReportEvaluationMetrics
    schema_pass_rate: float | None = Field(default=None, alias="schemaPassRate")
    schema_record_count: int = Field(alias="schemaRecordCount")
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


class AnalysisJobDebugResponse(BaseModel):
    job_id: str = Field(alias="jobId")
    status: str
    workflow_trace: list[AnalysisLogRecord] = Field(alias="workflowTrace")
    fallback_events: list[FallbackEvent] = Field(alias="fallbackEvents")
    mock_usage: list[MockUsageRecord] = Field(alias="mockUsage")
    schema_validation: list[SchemaValidationRecord] = Field(alias="schemaValidation")
    boundary_warnings: list[BoundaryWarning] = Field(alias="boundaryWarnings")
    retrieval_trace: list[RetrievalStepTrace] = Field(default_factory=list, alias="retrievalTrace")
    retrieval_items: list[RetrievalItemTrace] = Field(default_factory=list, alias="retrievalItems")
    context_assembly_trace: ContextAssemblyTrace | None = Field(
        default=None,
        alias="contextAssemblyTrace",
    )
    evaluation_trace: EvaluationTrace | None = Field(default=None, alias="evaluationTrace")

    model_config = {"populate_by_name": True}

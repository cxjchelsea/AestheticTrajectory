from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.analysis_log import AnalysisLogRecord


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


class AnalysisJobDebugResponse(BaseModel):
    job_id: str = Field(alias="jobId")
    status: str
    workflow_trace: list[AnalysisLogRecord] = Field(alias="workflowTrace")
    fallback_events: list[FallbackEvent] = Field(alias="fallbackEvents")
    mock_usage: list[MockUsageRecord] = Field(alias="mockUsage")
    schema_validation: list[SchemaValidationRecord] = Field(alias="schemaValidation")
    boundary_warnings: list[BoundaryWarning] = Field(alias="boundaryWarnings")

    model_config = {"populate_by_name": True}

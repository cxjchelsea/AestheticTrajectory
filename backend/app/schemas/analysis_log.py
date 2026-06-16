from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AnalysisLogStatus = Literal["running", "success", "failed", "skipped"]


class AnalysisLogRecord(BaseModel):
    id: str
    job_id: str = Field(alias="jobId")
    step_id: str = Field(alias="stepId")
    status: AnalysisLogStatus
    model_name: str | None = Field(default=None, alias="modelName")
    prompt_version: str | None = Field(default=None, alias="promptVersion")
    latency_ms: int | None = Field(default=None, alias="latencyMs")
    error_type: str | None = Field(default=None, alias="errorType")
    error_message: str | None = Field(default=None, alias="errorMessage")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}

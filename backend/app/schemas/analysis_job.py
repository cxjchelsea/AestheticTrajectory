from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


AnalysisJobStatus = Literal[
    "created",
    "queued",
    "running",
    "feature_extracting",
    "embedding_generating",
    "vector_writing",
    "similarity_grouping",
    "interpreting",
    "report_generating",
    "completed",
    "failed",
    "partial_failed",
    "cancelled",
]


class CreateAnalysisJobRequest(BaseModel):
    input_ids: list[str] = Field(alias="inputIds", min_length=3, max_length=12)

    model_config = {"populate_by_name": True}


class AnalysisJobResponse(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    status: AnalysisJobStatus
    input_count: int = Field(alias="inputCount")
    error_message: str | None = Field(default=None, alias="errorMessage")
    report_id: str | None = Field(default=None, alias="reportId")
    created_at: datetime = Field(alias="createdAt")
    started_at: datetime | None = Field(default=None, alias="startedAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")

    model_config = {"populate_by_name": True}

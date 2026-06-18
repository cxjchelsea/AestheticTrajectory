from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.timeline import TimelineSummaryPeriod


OBSERVATION_DISCLAIMER = (
    "观察摘要只聚合已有报告、时间轴与反馈证据，用于辅助理解审美变化，不构成人格、心理或能力判断。"
)

ObservationStatus = Literal["running", "completed", "abstained", "failed"]


class ObservationQuestion(BaseModel):
    text: str
    evidence_refs: list[str] = Field(default_factory=list, alias="evidenceRefs")

    model_config = {"populate_by_name": True}


class CreateObservationRequest(BaseModel):
    trigger_source: str = Field(default="profile_page", alias="triggerSource")
    period: TimelineSummaryPeriod = "week"

    model_config = {"populate_by_name": True}


class ObservationSession(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    status: ObservationStatus
    trigger_source: str = Field(alias="triggerSource")
    period: TimelineSummaryPeriod | None = None
    summary: str | None = None
    questions: list[ObservationQuestion] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list, alias="evidenceRefs")
    message: str | None = None
    disclaimer: str = OBSERVATION_DISCLAIMER
    created_at: datetime = Field(alias="createdAt")
    finished_at: datetime | None = Field(default=None, alias="finishedAt")

    model_config = {"populate_by_name": True}


class AgentActionLog(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    session_id: str = Field(alias="sessionId")
    step_index: int = Field(alias="stepIndex")
    tool_name: str = Field(alias="toolName")
    reason: str
    input_refs: list[str] = Field(default_factory=list, alias="inputRefs")
    output_refs: list[str] = Field(default_factory=list, alias="outputRefs")
    status: str
    latency_ms: int | None = Field(default=None, alias="latencyMs")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class AgentActionListResponse(BaseModel):
    user_id: str = Field(alias="userId")
    actions: list[AgentActionLog]
    total: int
    session_id: str | None = Field(default=None, alias="sessionId")

    model_config = {"populate_by_name": True}

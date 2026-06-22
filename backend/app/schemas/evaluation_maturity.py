from pydantic import BaseModel, Field


GROUPING_STABILITY_DISCLAIMER = (
    "该指标衡量本次 clustering 复算一致性，不代表长期偏好或绝对分类。"
)
FAILURE_REPLAY_DISCLAIMER = "只读回放，非自动重跑。"


class GroupingPairDetail(BaseModel):
    input_id_a: str = Field(alias="inputIdA")
    input_id_b: str = Field(alias="inputIdB")
    persisted_same_group: bool = Field(alias="persistedSameGroup")
    recomputed_same_group: bool = Field(alias="recomputedSameGroup")
    consistent: bool

    model_config = {"populate_by_name": True}


class GroupingStabilityResponse(BaseModel):
    report_id: str = Field(alias="reportId")
    score: float | None = None
    pair_count: int = Field(alias="pairCount")
    consistent_pair_count: int = Field(alias="consistentPairCount")
    persisted_group_count: int = Field(alias="persistedGroupCount")
    recomputed_group_count: int = Field(alias="recomputedGroupCount")
    pair_details: list[GroupingPairDetail] = Field(default_factory=list, alias="pairDetails")
    message: str | None = None
    disclaimer: str = GROUPING_STABILITY_DISCLAIMER

    model_config = {"populate_by_name": True}


class FailureReplayFallback(BaseModel):
    fallback_type: str = Field(alias="fallbackType")
    original_error: str = Field(alias="originalError")
    fallback_action: str = Field(alias="fallbackAction")
    severity: str
    developer_message: str = Field(alias="developerMessage")

    model_config = {"populate_by_name": True}


class FailureReplayStep(BaseModel):
    step_id: str = Field(alias="stepId")
    status: str
    error_type: str | None = Field(default=None, alias="errorType")
    error_message: str | None = Field(default=None, alias="errorMessage")
    latency_ms: int | None = Field(default=None, alias="latencyMs")
    fallbacks: list[FailureReplayFallback] = Field(default_factory=list)
    developer_summary: str = Field(alias="developerSummary")

    model_config = {"populate_by_name": True}


class FailureReplayResponse(BaseModel):
    job_id: str = Field(alias="jobId")
    failed: bool
    steps: list[FailureReplayStep]
    message: str | None = None
    replay_disclaimer: str = Field(default=FAILURE_REPLAY_DISCLAIMER, alias="replayDisclaimer")

    model_config = {"populate_by_name": True}


class GroupingStabilityTrace(BaseModel):
    report_id: str | None = Field(default=None, alias="reportId")
    score: float | None = None
    pair_count: int = Field(alias="pairCount")
    consistent_pair_count: int = Field(alias="consistentPairCount")
    developer_message: str = Field(alias="developerMessage")
    disclaimer: str = GROUPING_STABILITY_DISCLAIMER

    model_config = {"populate_by_name": True}

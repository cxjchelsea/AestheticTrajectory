from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.feature import InputFeature
from app.schemas.history_context import PersonalHistoryContext
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup


class Insight(BaseModel):
    insight_id: str = Field(alias="insightId")
    title: str
    observation: str
    evidence_refs: list[str] = Field(alias="evidenceRefs")
    interpretation: str
    uncertainty: str
    confidence: float = Field(ge=0, le=1)

    model_config = {"populate_by_name": True}


class ReportResponse(BaseModel):
    report_id: str = Field(alias="reportId")
    title: str
    summary: str
    low_level_features: list[InputFeature] = Field(alias="lowLevelFeatures")
    similarity_groups: list[SimilarityGroup] = Field(alias="similarityGroups")
    possible_interpretations: list[PossibleInterpretation] = Field(alias="possibleInterpretations")
    insights: list[Insight]
    disclaimer: str
    history_context: PersonalHistoryContext | None = Field(default=None, alias="historyContext")

    model_config = {"populate_by_name": True}


class ReportSummary(BaseModel):
    report_id: str = Field(alias="reportId")
    job_id: str | None = Field(default=None, alias="jobId")
    title: str
    summary: str
    input_count: int = Field(alias="inputCount")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class ReportHistoryResponse(BaseModel):
    reports: list[ReportSummary]
    total: int
    limit: int
    offset: int

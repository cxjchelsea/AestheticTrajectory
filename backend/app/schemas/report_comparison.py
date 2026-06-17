from datetime import datetime

from pydantic import BaseModel, Field


class ComparisonReportRef(BaseModel):
    report_id: str = Field(alias="reportId")
    title: str
    summary: str
    created_at: datetime | None = Field(default=None, alias="createdAt")

    model_config = {"populate_by_name": True}


class ReportFeatureChange(BaseModel):
    change_type: str = Field(alias="changeType")
    label: str
    previous_count: int = Field(alias="previousCount")
    current_count: int = Field(alias="currentCount")
    evidence_refs: list[str] = Field(alias="evidenceRefs")
    note: str

    model_config = {"populate_by_name": True}


class ReportInterpretationChange(BaseModel):
    change_type: str = Field(alias="changeType")
    label: str
    evidence_refs: list[str] = Field(alias="evidenceRefs")
    note: str

    model_config = {"populate_by_name": True}


class ReportComparisonResponse(BaseModel):
    user_id: str = Field(alias="userId")
    previous_report: ComparisonReportRef | None = Field(default=None, alias="previousReport")
    current_report: ComparisonReportRef | None = Field(default=None, alias="currentReport")
    feature_changes: list[ReportFeatureChange] = Field(default_factory=list, alias="featureChanges")
    interpretation_changes: list[ReportInterpretationChange] = Field(
        default_factory=list,
        alias="interpretationChanges",
    )
    summary: str | None = None
    message: str | None = None
    disclaimer: str

    model_config = {"populate_by_name": True}

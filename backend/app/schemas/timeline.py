from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TimelineEventType = Literal[
    "new_interpretation",
    "interpretation_decline",
    "feature_shift",
    "style_shift",
    "contradiction_detected",
    "stable_preference",
    "report_completed",
]

TimelineSummaryPeriod = Literal["week", "month"]


class TimelineEvidence(BaseModel):
    evidence_refs: list[str] = Field(alias="evidenceRefs")
    comparison_ref: str | None = Field(default=None, alias="comparisonRef")
    feature_keys: list[str] = Field(default_factory=list, alias="featureKeys")
    insight_ids: list[str] = Field(default_factory=list, alias="insightIds")
    feedback_ids: list[str] = Field(default_factory=list, alias="feedbackIds")
    note: str | None = None
    dedupe_key: str = Field(alias="dedupeKey")

    model_config = {"populate_by_name": True}


class TimelineEvent(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    event_type: TimelineEventType = Field(alias="eventType")
    title: str
    description: str | None = None
    related_report_ids: list[str] = Field(alias="relatedReportIds")
    related_insight_ids: list[str] = Field(default_factory=list, alias="relatedInsightIds")
    related_feedback_ids: list[str] = Field(default_factory=list, alias="relatedFeedbackIds")
    evidence: TimelineEvidence
    occurred_at: datetime = Field(alias="occurredAt")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class TimelineEventDraft(BaseModel):
    user_id: str = Field(alias="userId")
    event_type: TimelineEventType = Field(alias="eventType")
    title: str
    description: str | None = None
    related_report_ids: list[str] = Field(alias="relatedReportIds")
    related_insight_ids: list[str] = Field(default_factory=list, alias="relatedInsightIds")
    related_feedback_ids: list[str] = Field(default_factory=list, alias="relatedFeedbackIds")
    evidence: TimelineEvidence
    occurred_at: datetime = Field(alias="occurredAt")

    model_config = {"populate_by_name": True}


class TimelineListResponse(BaseModel):
    user_id: str = Field(alias="userId")
    events: list[TimelineEvent]
    total: int
    limit: int
    offset: int
    message: str | None = None
    disclaimer: str

    model_config = {"populate_by_name": True}


class TimelineSummaryHighlight(BaseModel):
    event_type: TimelineEventType = Field(alias="eventType")
    title: str
    occurred_at: datetime = Field(alias="occurredAt")
    evidence_refs: list[str] = Field(alias="evidenceRefs")

    model_config = {"populate_by_name": True}


class TimelineSummaryResponse(BaseModel):
    user_id: str = Field(alias="userId")
    period: TimelineSummaryPeriod
    summary_text: str = Field(alias="summaryText")
    event_count: int = Field(alias="eventCount")
    report_count: int = Field(alias="reportCount")
    highlights: list[TimelineSummaryHighlight]
    message: str | None = None
    disclaimer: str

    model_config = {"populate_by_name": True}

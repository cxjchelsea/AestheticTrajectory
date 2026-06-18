from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ProfileItemStatus = Literal["stable", "recent", "weakening", "rejected", "uncertain", "inactive", "hidden", "deleted"]
ProfileEvidenceType = Literal["feature", "report", "interpretation", "insight", "feedback"]
ProfileEvidenceDirection = Literal["positive", "negative", "uncertain", "conflict"]


class ProfileEvidence(BaseModel):
    id: str
    evidence_type: ProfileEvidenceType = Field(alias="evidenceType")
    evidence_id: str = Field(alias="evidenceId")
    direction: ProfileEvidenceDirection
    weight_delta: float = Field(alias="weightDelta")
    note: str
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class ProfileItem(BaseModel):
    id: str
    key: str
    label: str
    status: ProfileItemStatus
    weight: float = Field(ge=-1, le=1)
    confidence: float = Field(ge=0, le=1)
    source_count: int = Field(alias="sourceCount", ge=1)
    last_seen_at: datetime = Field(alias="lastSeenAt")
    evidence: list[ProfileEvidence] = Field(min_length=1)

    model_config = {"populate_by_name": True}


class UserProfile(BaseModel):
    id: str
    summary: str
    version: str
    items: list[ProfileItem]
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class ProfileResponse(BaseModel):
    user_id: str = Field(alias="userId")
    profile: UserProfile | None = None
    message: str | None = None

    model_config = {"populate_by_name": True}

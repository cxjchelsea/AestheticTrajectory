from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


FeedbackRating = Literal["not_me", "unsure", "somewhat_me", "very_me"]


class CreateInsightFeedbackRequest(BaseModel):
    rating: FeedbackRating
    comment: str | None = None


class InsightFeedbackResponse(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    insight_id: str = Field(alias="insightId")
    interpretation_id: str | None = Field(default=None, alias="interpretationId")
    rating: FeedbackRating
    comment: str | None
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}

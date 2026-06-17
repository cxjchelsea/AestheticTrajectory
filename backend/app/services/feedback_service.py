from app.schemas.common import new_id, utc_now
from app.schemas.feedback import CreateInsightFeedbackRequest, InsightFeedbackResponse


class FeedbackTargetNotFoundError(ValueError):
    pass


class FeedbackService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_feedback(self, insight_id: str) -> InsightFeedbackResponse | None:
        return self.repository.get_for_target("user_anonymous", insight_id)

    def create_feedback(self, insight_id: str, request: CreateInsightFeedbackRequest) -> InsightFeedbackResponse:
        if not self.repository.insight_exists(insight_id):
            raise FeedbackTargetNotFoundError(f"Insight not found: {insight_id}")

        existing = self.repository.get_for_target("user_anonymous", insight_id)
        feedback = InsightFeedbackResponse(
            id=existing.id if existing else new_id("feedback"),
            userId="user_anonymous",
            insightId=insight_id,
            interpretationId=existing.interpretation_id if existing else None,
            rating=request.rating,
            comment=request.comment,
            createdAt=utc_now(),
        )
        return self.repository.save(feedback)

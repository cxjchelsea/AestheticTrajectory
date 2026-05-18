from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.memory_store import MemoryStore
from app.schemas.common import new_id, utc_now
from app.schemas.feedback import CreateInsightFeedbackRequest, InsightFeedbackResponse


class FeedbackService:
    def __init__(self, store: MemoryStore) -> None:
        self.repository = FeedbackRepository(store)

    def create_feedback(self, insight_id: str, request: CreateInsightFeedbackRequest) -> InsightFeedbackResponse:
        feedback = InsightFeedbackResponse(
            id=new_id("feedback"),
            userId="user_anonymous",
            insightId=insight_id,
            interpretationId=None,
            rating=request.rating,
            comment=request.comment,
            createdAt=utc_now(),
        )
        return self.repository.save(feedback)

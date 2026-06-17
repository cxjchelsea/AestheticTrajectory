from app.repositories.memory_store import MemoryStore
from app.schemas.feedback import InsightFeedbackResponse


class FeedbackRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def insight_exists(self, insight_id: str) -> bool:
        return any(
            insight.insight_id == insight_id
            for report in self.store.reports.values()
            for insight in report.insights
        )

    def get_for_target(self, user_id: str, insight_id: str) -> InsightFeedbackResponse | None:
        matches = [
            feedback
            for feedback in self.store.feedback.values()
            if feedback.user_id == user_id and feedback.insight_id == insight_id
        ]
        if not matches:
            return None
        return max(matches, key=lambda feedback: feedback.created_at)

    def save(self, feedback: InsightFeedbackResponse) -> InsightFeedbackResponse:
        for existing_id, existing in list(self.store.feedback.items()):
            if existing.user_id == feedback.user_id and existing.insight_id == feedback.insight_id:
                del self.store.feedback[existing_id]
        self.store.feedback[feedback.id] = feedback
        return feedback

from app.repositories.memory_store import MemoryStore
from app.schemas.feedback import InsightFeedbackResponse


class FeedbackRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, feedback: InsightFeedbackResponse) -> InsightFeedbackResponse:
        self.store.feedback[feedback.id] = feedback
        return feedback

from app.repositories.memory_store import MemoryStore
from app.schemas.feedback import InsightFeedbackResponse


class FeedbackRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def insight_exists(self, insight_id: str) -> bool:
        return self.find_insight_context(insight_id) is not None

    def find_insight_context(self, insight_id: str) -> tuple[str, str | None] | None:
        for report_id, report in self.store.reports.items():
            for insight in report.insights:
                if insight.insight_id == insight_id:
                    return insight.title, report_id
        return None

    def get_insight_user_id(self, insight_id: str) -> str | None:
        context = self.find_insight_context(insight_id)
        if context is None:
            return None
        _, report_id = context
        if report_id is None:
            return None
        metadata = self.store.report_metadata.get(report_id, {})
        user_id = metadata.get("user_id")
        return user_id if isinstance(user_id, str) else None

    def list_by_user(self, user_id: str) -> list[InsightFeedbackResponse]:
        return [feedback for feedback in self.store.feedback.values() if feedback.user_id == user_id]

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

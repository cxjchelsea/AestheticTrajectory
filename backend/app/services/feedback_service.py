from app.schemas.common import new_id, utc_now
from app.schemas.feedback import CreateInsightFeedbackRequest, InsightFeedbackResponse
from app.services.timeline_builder import build_feedback_decline_event


class FeedbackTargetNotFoundError(ValueError):
    pass


class FeedbackAccessDeniedError(ValueError):
    pass


class FeedbackService:
    def __init__(self, repository, timeline_repository=None) -> None:
        self.repository = repository
        self.timeline_repository = timeline_repository

    def get_feedback(self, insight_id: str, user_id: str) -> InsightFeedbackResponse | None:
        self._assert_insight_access(insight_id, user_id)
        return self.repository.get_for_target(user_id, insight_id)

    def create_feedback(
        self,
        insight_id: str,
        request: CreateInsightFeedbackRequest,
        user_id: str,
    ) -> InsightFeedbackResponse:
        if not self.repository.insight_exists(insight_id):
            raise FeedbackTargetNotFoundError(f"Insight not found: {insight_id}")
        self._assert_insight_access(insight_id, user_id)

        existing = self.repository.get_for_target(user_id, insight_id)
        feedback = InsightFeedbackResponse(
            id=existing.id if existing else new_id("feedback"),
            userId=user_id,
            insightId=insight_id,
            interpretationId=existing.interpretation_id if existing else None,
            rating=request.rating,
            comment=request.comment,
            createdAt=utc_now(),
        )
        saved = self.repository.save(feedback)
        self._append_feedback_timeline_event(saved)
        return saved

    def _assert_insight_access(self, insight_id: str, user_id: str) -> None:
        owner_user_id = self.repository.get_insight_user_id(insight_id)
        if owner_user_id is not None and owner_user_id != user_id:
            raise FeedbackAccessDeniedError("Access denied for requested insight")

    def _append_feedback_timeline_event(self, feedback: InsightFeedbackResponse) -> None:
        if self.timeline_repository is None or feedback.rating != "not_me":
            return
        context = self.repository.find_insight_context(feedback.insight_id)
        if context is None:
            return
        insight_title, report_id = context
        draft = build_feedback_decline_event(
            feedback.user_id,
            feedback,
            insight_title,
            report_id,
            feedback.created_at,
        )
        if draft is not None:
            self.timeline_repository.append_events([draft])

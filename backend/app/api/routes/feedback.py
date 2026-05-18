from fastapi import APIRouter, Depends

from app.api.deps import get_feedback_service
from app.schemas.feedback import CreateInsightFeedbackRequest, InsightFeedbackResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(tags=["feedback"])


@router.post("/insights/{insight_id}/feedback", response_model=InsightFeedbackResponse)
def create_feedback(
    insight_id: str,
    request: CreateInsightFeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> InsightFeedbackResponse:
    return service.create_feedback(insight_id, request)

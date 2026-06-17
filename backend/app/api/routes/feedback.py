from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_feedback_service
from app.schemas.feedback import CreateInsightFeedbackRequest, InsightFeedbackResponse
from app.services.feedback_service import FeedbackService, FeedbackTargetNotFoundError

router = APIRouter(tags=["feedback"])


@router.get("/insights/{insight_id}/feedback", response_model=InsightFeedbackResponse | None)
def get_feedback(
    insight_id: str,
    service: FeedbackService = Depends(get_feedback_service),
) -> InsightFeedbackResponse | None:
    return service.get_feedback(insight_id)


@router.post("/insights/{insight_id}/feedback", response_model=InsightFeedbackResponse)
def create_feedback(
    insight_id: str,
    request: CreateInsightFeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
) -> InsightFeedbackResponse:
    try:
        return service.create_feedback(insight_id, request)
    except FeedbackTargetNotFoundError as error:
        raise HTTPException(status_code=404, detail="Insight not found") from error

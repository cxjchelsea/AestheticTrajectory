from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_feedback_service
from app.core.auth import CurrentUser
from app.schemas.feedback import CreateInsightFeedbackRequest, InsightFeedbackResponse
from app.services.feedback_service import FeedbackAccessDeniedError, FeedbackService, FeedbackTargetNotFoundError

router = APIRouter(tags=["feedback"])


@router.get("/insights/{insight_id}/feedback", response_model=InsightFeedbackResponse | None)
def get_feedback(
    insight_id: str,
    service: FeedbackService = Depends(get_feedback_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> InsightFeedbackResponse | None:
    try:
        return service.get_feedback(insight_id, current_user.user_id)
    except FeedbackAccessDeniedError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


@router.post("/insights/{insight_id}/feedback", response_model=InsightFeedbackResponse)
def create_feedback(
    insight_id: str,
    request: CreateInsightFeedbackRequest,
    service: FeedbackService = Depends(get_feedback_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> InsightFeedbackResponse:
    try:
        return service.create_feedback(insight_id, request, current_user.user_id)
    except FeedbackTargetNotFoundError as error:
        raise HTTPException(status_code=404, detail="Insight not found") from error
    except FeedbackAccessDeniedError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error

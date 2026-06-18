from fastapi import APIRouter, Depends, Query

from app.api.deps import get_timeline_service
from app.schemas.timeline import TimelineListResponse, TimelineSummaryPeriod, TimelineSummaryResponse
from app.services.timeline_service import TimelineService

router = APIRouter(tags=["timeline"])


@router.get("/users/{user_id}/timeline", response_model=TimelineListResponse)
def list_user_timeline(
    user_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineListResponse:
    return service.list_timeline(user_id, limit=limit, offset=offset)


@router.get("/users/{user_id}/timeline/summary", response_model=TimelineSummaryResponse)
def get_user_timeline_summary(
    user_id: str,
    period: TimelineSummaryPeriod = Query(default="week"),
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineSummaryResponse:
    return service.get_summary(user_id, period)

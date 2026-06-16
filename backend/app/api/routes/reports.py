from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_report_service
from app.schemas.report import ReportHistoryResponse, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])


@router.get("/users/{user_id}/reports", response_model=ReportHistoryResponse)
def list_user_reports(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    service: ReportService = Depends(get_report_service),
) -> ReportHistoryResponse:
    return service.list_user_reports(user_id, limit, offset)


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    report = service.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

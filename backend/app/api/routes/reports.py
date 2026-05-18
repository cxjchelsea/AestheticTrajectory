from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_report_service
from app.schemas.report import ReportResponse
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> ReportResponse:
    report = service.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

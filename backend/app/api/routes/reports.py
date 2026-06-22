from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user, get_report_service, require_user_scope
from app.core.auth import CurrentUser
from app.schemas.report import ReportHistoryResponse, ReportResponse
from app.schemas.report_comparison import ReportComparisonResponse
from app.schemas.report_evaluation import ReportEvaluationResponse
from app.schemas.evaluation_maturity import GroupingStabilityResponse
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])


def _assert_report_access(report_id: str, service: ReportService, current_user: CurrentUser) -> None:
    owner_user_id = service.get_report_user_id(report_id)
    if owner_user_id is None:
        raise HTTPException(status_code=404, detail="Report not found")
    current_user.assert_resource_owner(owner_user_id)


@router.get("/users/{user_id}/reports/comparison/latest", response_model=ReportComparisonResponse)
def compare_latest_user_reports(
    user_id: str,
    service: ReportService = Depends(get_report_service),
    _: str = Depends(require_user_scope),
) -> ReportComparisonResponse:
    return service.compare_latest_reports(user_id)


@router.get("/users/{user_id}/reports", response_model=ReportHistoryResponse)
def list_user_reports(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    service: ReportService = Depends(get_report_service),
    _: str = Depends(require_user_scope),
) -> ReportHistoryResponse:
    return service.list_user_reports(user_id, limit, offset)


@router.get("/reports/{report_id}/grouping-stability", response_model=GroupingStabilityResponse)
def get_report_grouping_stability(
    report_id: str,
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> GroupingStabilityResponse:
    _assert_report_access(report_id, service, current_user)
    result = service.get_grouping_stability(report_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return result


@router.get("/reports/{report_id}/evaluation", response_model=ReportEvaluationResponse)
def get_report_evaluation(
    report_id: str,
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> ReportEvaluationResponse:
    _assert_report_access(report_id, service, current_user)
    evaluation = service.get_report_evaluation(report_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return evaluation


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> ReportResponse:
    _assert_report_access(report_id, service, current_user)
    report = service.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

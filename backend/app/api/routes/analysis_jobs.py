from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_analysis_job_service, get_current_user
from app.core.auth import CurrentUser
from app.schemas.analysis_debug import AnalysisJobDebugResponse
from app.schemas.evaluation_maturity import FailureReplayResponse
from app.schemas.analysis_job import AnalysisJobResponse, CreateAnalysisJobRequest
from app.services.analysis_job_service import AnalysisJobService, InputAccessDeniedError

router = APIRouter(tags=["analysis-jobs"])


def _assert_job_access(job: AnalysisJobResponse | None, current_user: CurrentUser) -> AnalysisJobResponse:
    if job is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    current_user.assert_resource_owner(job.user_id)
    return job


@router.post("/analysis-jobs", response_model=AnalysisJobResponse)
def create_analysis_job(
    request: CreateAnalysisJobRequest,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisJobResponse:
    try:
        return service.create_job(request, current_user.user_id)
    except InputAccessDeniedError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error


@router.get("/analysis-jobs/{job_id}", response_model=AnalysisJobResponse)
def get_analysis_job(
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisJobResponse:
    return _assert_job_access(service.get_job(job_id), current_user)


@router.get("/analysis-jobs/{job_id}/failure-replay", response_model=FailureReplayResponse)
def get_analysis_job_failure_replay(
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> FailureReplayResponse:
    _assert_job_access(service.get_job(job_id), current_user)
    replay = service.get_failure_replay(job_id)
    if replay is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return replay


@router.get("/analysis-jobs/{job_id}/debug", response_model=AnalysisJobDebugResponse)
def get_analysis_job_debug(
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> AnalysisJobDebugResponse:
    _assert_job_access(service.get_job(job_id), current_user)
    debug = service.get_debug(job_id, current_user)
    if debug is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return debug

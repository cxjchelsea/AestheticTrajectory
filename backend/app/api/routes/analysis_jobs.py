from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_analysis_job_service
from app.schemas.analysis_debug import AnalysisJobDebugResponse
from app.schemas.evaluation_maturity import FailureReplayResponse
from app.schemas.analysis_job import AnalysisJobResponse, CreateAnalysisJobRequest
from app.services.analysis_job_service import AnalysisJobService

router = APIRouter(tags=["analysis-jobs"])


@router.post("/analysis-jobs", response_model=AnalysisJobResponse)
def create_analysis_job(
    request: CreateAnalysisJobRequest,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> AnalysisJobResponse:
    return service.create_job(request)


@router.get("/analysis-jobs/{job_id}", response_model=AnalysisJobResponse)
def get_analysis_job(
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> AnalysisJobResponse:
    job = service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return job


@router.get("/analysis-jobs/{job_id}/failure-replay", response_model=FailureReplayResponse)
def get_analysis_job_failure_replay(
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> FailureReplayResponse:
    replay = service.get_failure_replay(job_id)
    if replay is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return replay


@router.get("/analysis-jobs/{job_id}/debug", response_model=AnalysisJobDebugResponse)
def get_analysis_job_debug(
    job_id: str,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> AnalysisJobDebugResponse:
    debug = service.get_debug(job_id)
    if debug is None:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return debug

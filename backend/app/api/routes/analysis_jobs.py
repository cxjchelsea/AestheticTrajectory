from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_analysis_job_service
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

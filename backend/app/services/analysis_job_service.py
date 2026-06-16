from app.schemas.analysis_job import AnalysisJobResponse, CreateAnalysisJobRequest
from app.schemas.common import new_id, utc_now
from app.workflows.aesthetic_analysis_v1 import run_mock_aesthetic_analysis


class AnalysisJobService:
    def __init__(self, job_repository, input_repository, workflow_persistence) -> None:
        self.job_repository = job_repository
        self.input_repository = input_repository
        self.workflow_persistence = workflow_persistence

    def create_job(self, request: CreateAnalysisJobRequest) -> AnalysisJobResponse:
        now = utc_now()
        job = AnalysisJobResponse(
            id=new_id("job"),
            userId="user_anonymous",
            status="created",
            inputCount=len(request.input_ids),
            errorMessage=None,
            reportId=None,
            createdAt=now,
            startedAt=now,
            finishedAt=None,
        )
        self.job_repository.save(job)
        inputs = self.input_repository.get_many(request.input_ids)
        result = run_mock_aesthetic_analysis(job, inputs, self.workflow_persistence)
        return self.job_repository.save(result)

    def get_job(self, job_id: str) -> AnalysisJobResponse | None:
        return self.job_repository.get(job_id)

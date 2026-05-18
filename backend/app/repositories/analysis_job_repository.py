from app.repositories.memory_store import MemoryStore
from app.schemas.analysis_job import AnalysisJobResponse


class AnalysisJobRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, job: AnalysisJobResponse) -> AnalysisJobResponse:
        self.store.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> AnalysisJobResponse | None:
        return self.store.jobs.get(job_id)

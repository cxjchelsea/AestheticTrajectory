from app.repositories.memory_store import MemoryStore
from app.schemas.analysis_log import AnalysisLogRecord


class AnalysisLogRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, log: AnalysisLogRecord) -> AnalysisLogRecord:
        self.store.analysis_logs[log.id] = log
        return log

    def get_for_job(self, job_id: str) -> list[AnalysisLogRecord]:
        return [log for log in self.store.analysis_logs.values() if log.job_id == job_id]

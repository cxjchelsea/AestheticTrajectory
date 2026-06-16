from app.repositories.memory_store import MemoryStore
from app.schemas.report import ReportResponse


class ReportRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, report: ReportResponse, user_id: str | None = None, job_id: str | None = None) -> ReportResponse:
        self.store.reports[report.report_id] = report
        return report

    def get(self, report_id: str) -> ReportResponse | None:
        return self.store.reports.get(report_id)

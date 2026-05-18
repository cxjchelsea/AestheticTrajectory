from app.repositories.memory_store import MemoryStore
from app.repositories.report_repository import ReportRepository
from app.schemas.report import ReportResponse


class ReportService:
    def __init__(self, store: MemoryStore) -> None:
        self.repository = ReportRepository(store)

    def get_report(self, report_id: str) -> ReportResponse | None:
        return self.repository.get(report_id)

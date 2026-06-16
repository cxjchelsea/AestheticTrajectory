from app.schemas.report import ReportResponse


class ReportService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_report(self, report_id: str) -> ReportResponse | None:
        return self.repository.get(report_id)

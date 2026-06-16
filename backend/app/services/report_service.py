from app.schemas.report import ReportHistoryResponse, ReportResponse


class ReportService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_report(self, report_id: str) -> ReportResponse | None:
        return self.repository.get(report_id)

    def list_user_reports(self, user_id: str, limit: int = 20, offset: int = 0) -> ReportHistoryResponse:
        return self.repository.list_by_user(user_id, limit, offset)

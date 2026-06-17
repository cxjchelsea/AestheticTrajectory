from app.schemas.report import ReportHistoryResponse, ReportResponse
from app.schemas.report_comparison import ReportComparisonResponse
from app.services.report_comparison import build_latest_report_comparison


class ReportService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_report(self, report_id: str) -> ReportResponse | None:
        return self.repository.get(report_id)

    def list_user_reports(self, user_id: str, limit: int = 20, offset: int = 0) -> ReportHistoryResponse:
        return self.repository.list_by_user(user_id, limit, offset)

    def compare_latest_reports(self, user_id: str) -> ReportComparisonResponse:
        reports = self.repository.list_recent_by_user(user_id, limit=2)
        return build_latest_report_comparison(user_id, reports)

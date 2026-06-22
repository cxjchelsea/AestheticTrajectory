from app.schemas.report import ReportHistoryResponse, ReportResponse
from app.schemas.report_comparison import ReportComparisonResponse
from app.schemas.report_evaluation import ReportEvaluationResponse
from app.schemas.evaluation_maturity import GroupingStabilityResponse
from app.services.grouping_stability import build_grouping_stability
from app.services.report_comparison import build_latest_report_comparison
from app.services.report_evaluation import build_report_evaluation
from app.services.schema_validation_summary import build_schema_validation_records


class ReportService:
    def __init__(
        self,
        repository,
        feedback_repository=None,
        analysis_log_repository=None,
        input_repository=None,
    ) -> None:
        self.repository = repository
        self.feedback_repository = feedback_repository
        self.analysis_log_repository = analysis_log_repository
        self.input_repository = input_repository

    def get_report(self, report_id: str) -> ReportResponse | None:
        return self.repository.get(report_id)

    def get_report_user_id(self, report_id: str) -> str | None:
        return self.repository.get_user_id(report_id)

    def list_user_reports(self, user_id: str, limit: int = 20, offset: int = 0) -> ReportHistoryResponse:
        return self.repository.list_by_user(user_id, limit, offset)

    def compare_latest_reports(self, user_id: str) -> ReportComparisonResponse:
        reports = self.repository.list_recent_by_user(user_id, limit=2)
        return build_latest_report_comparison(user_id, reports)

    def get_report_evaluation(self, report_id: str) -> ReportEvaluationResponse | None:
        report = self.repository.get(report_id)
        if report is None:
            return None

        feedback = []
        user_id = self.repository.get_user_id(report_id)
        if self.feedback_repository is not None and user_id is not None:
            feedback = self.feedback_repository.list_by_user(user_id)

        schema_validation = []
        job_id = self.repository.get_job_id(report_id)
        if self.analysis_log_repository is not None and job_id is not None:
            logs = self.analysis_log_repository.get_for_job(job_id)
            schema_validation = build_schema_validation_records(logs)

        return build_report_evaluation(report, feedback, schema_validation)

    def get_grouping_stability(self, report_id: str) -> GroupingStabilityResponse | None:
        report = self.repository.get(report_id)
        if report is None:
            return None
        if self.input_repository is None:
            return GroupingStabilityResponse(
                reportId=report_id,
                score=None,
                pairCount=0,
                consistentPairCount=0,
                persistedGroupCount=len(report.similarity_groups),
                recomputedGroupCount=0,
                message="Input repository unavailable; cannot recompute clustering.",
            )

        input_ids = [feature.input_id for feature in report.low_level_features]
        inputs = self.input_repository.get_many(input_ids)
        return build_grouping_stability(report, inputs)

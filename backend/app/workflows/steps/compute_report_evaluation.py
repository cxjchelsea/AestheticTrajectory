from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.report import ReportResponse
from app.schemas.report_evaluation import ReportEvaluationResponse
from app.services.schema_validation_summary import build_schema_validation_records
from app.services.report_evaluation import build_report_evaluation


def compute_report_evaluation(
    report: ReportResponse,
    job_id: str,
    analysis_log_repository,
    feedback: list[InsightFeedbackResponse] | None = None,
) -> ReportEvaluationResponse:
    logs = analysis_log_repository.get_for_job(job_id)
    schema_validation = build_schema_validation_records(logs)
    return build_report_evaluation(report, feedback or [], schema_validation)

from app.repositories.memory_store import store
from app.services.analysis_job_service import AnalysisJobService
from app.services.feedback_service import FeedbackService
from app.services.input_service import InputService
from app.services.report_service import ReportService


def get_input_service() -> InputService:
    return InputService(store)


def get_analysis_job_service() -> AnalysisJobService:
    return AnalysisJobService(store)


def get_report_service() -> ReportService:
    return ReportService(store)


def get_feedback_service() -> FeedbackService:
    return FeedbackService(store)

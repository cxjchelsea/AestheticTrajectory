from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_session
from app.repositories.analysis_job_repository import AnalysisJobRepository
from app.repositories.database_repositories import (
    DatabaseAnalysisJobRepository,
    DatabaseAnalysisLogRepository,
    DatabaseEmbeddingRecordRepository,
    DatabaseFeatureRepository,
    DatabaseFeedbackRepository,
    DatabaseInputRepository,
    DatabaseProfileRepository,
    DatabaseReportRepository,
)
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.input_repository import InputRepository
from app.repositories.memory_store import store
from app.repositories.profile_repository import ProfileRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.workflow_persistence import WorkflowPersistence
from app.services.analysis_job_service import AnalysisJobService
from app.services.feedback_service import FeedbackService
from app.services.input_service import InputService
from app.services.profile_service import ProfileService
from app.services.report_service import ReportService
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence


def get_input_service(session: Session = Depends(get_session)) -> InputService:
    if settings.repository_backend == "database":
        return InputService(DatabaseInputRepository(session))
    return InputService(InputRepository(store))


def get_analysis_job_service(session: Session = Depends(get_session)) -> AnalysisJobService:
    if settings.repository_backend == "database":
        workflow_persistence = WorkflowPersistence(
            feature_repository=DatabaseFeatureRepository(session),
            embedding_record_repository=DatabaseEmbeddingRecordRepository(session),
            report_repository=DatabaseReportRepository(session),
            analysis_log_repository=DatabaseAnalysisLogRepository(session),
            feedback_repository=DatabaseFeedbackRepository(session),
        )
        return AnalysisJobService(
            DatabaseAnalysisJobRepository(session),
            DatabaseInputRepository(session),
            workflow_persistence,
        )
    return AnalysisJobService(
        AnalysisJobRepository(store),
        InputRepository(store),
        memory_workflow_persistence(store),
    )


def get_report_service(session: Session = Depends(get_session)) -> ReportService:
    if settings.repository_backend == "database":
        return ReportService(DatabaseReportRepository(session))
    return ReportService(ReportRepository(store))


def get_feedback_service(session: Session = Depends(get_session)) -> FeedbackService:
    if settings.repository_backend == "database":
        return FeedbackService(DatabaseFeedbackRepository(session))
    return FeedbackService(FeedbackRepository(store))


def get_profile_service(session: Session = Depends(get_session)) -> ProfileService:
    if settings.repository_backend == "database":
        return ProfileService(DatabaseProfileRepository(session))
    return ProfileService(ProfileRepository(store))

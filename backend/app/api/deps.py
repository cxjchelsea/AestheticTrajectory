from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_session
from app.repositories.analysis_job_repository import AnalysisJobRepository
from app.repositories.analysis_log_repository import AnalysisLogRepository
from app.repositories.chroma_debug_store import chroma_write_results
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
from app.repositories.agent_repository import (
    AgentActionLogRepository,
    DatabaseAgentActionLogRepository,
    DatabaseObservationSessionRepository,
    ObservationSessionRepository,
)
from app.repositories.knowledge_graph_repository import DatabaseKnowledgeGraphRepository, KnowledgeGraphRepository
from app.repositories.external_import_repository import DatabaseExternalImportRepository, ExternalImportRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.input_repository import InputRepository
from app.repositories.memory_store import store
from app.repositories.profile_repository import ProfileRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.timeline_repository import DatabaseTimelineRepository, TimelineRepository
from app.repositories.workflow_persistence import WorkflowPersistence
from app.services.analysis_job_service import AnalysisJobService
from app.services.feedback_service import FeedbackService
from app.services.input_service import InputService
from app.services.profile_service import ProfileService
from app.services.report_service import ReportService
from app.services.knowledge_graph_query import KnowledgeGraphQueryService
from app.services.observation_service import ObservationService
from app.services.timeline_service import TimelineService
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
            timeline_repository=DatabaseTimelineRepository(session),
            knowledge_graph_repository=DatabaseKnowledgeGraphRepository(session),
            chroma_write_results=chroma_write_results,
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
        return ReportService(
            DatabaseReportRepository(session),
            DatabaseFeedbackRepository(session),
            DatabaseAnalysisLogRepository(session),
        )
    return ReportService(
        ReportRepository(store),
        FeedbackRepository(store),
        AnalysisLogRepository(store),
    )


def get_feedback_service(session: Session = Depends(get_session)) -> FeedbackService:
    if settings.repository_backend == "database":
        return FeedbackService(
            DatabaseFeedbackRepository(session),
            DatabaseTimelineRepository(session),
        )
    return FeedbackService(FeedbackRepository(store), TimelineRepository(store))


def get_profile_service(session: Session = Depends(get_session)) -> ProfileService:
    if settings.repository_backend == "database":
        return ProfileService(
            DatabaseProfileRepository(session),
            DatabaseTimelineRepository(session),
        )
    return ProfileService(ProfileRepository(store), TimelineRepository(store))


def get_timeline_service(session: Session = Depends(get_session)) -> TimelineService:
    if settings.repository_backend == "database":
        return TimelineService(DatabaseTimelineRepository(session), DatabaseReportRepository(session))
    return TimelineService(TimelineRepository(store), ReportRepository(store))


def get_knowledge_graph_service(session: Session = Depends(get_session)) -> KnowledgeGraphQueryService:
    if settings.repository_backend == "database":
        return KnowledgeGraphQueryService(DatabaseKnowledgeGraphRepository(session))
    return KnowledgeGraphQueryService(KnowledgeGraphRepository())


def get_observation_service(
    session: Session = Depends(get_session),
    report_service: ReportService = Depends(get_report_service),
    timeline_service: TimelineService = Depends(get_timeline_service),
    profile_service: ProfileService = Depends(get_profile_service),
    knowledge_service: KnowledgeGraphQueryService = Depends(get_knowledge_graph_service),
) -> ObservationService:
    if settings.repository_backend == "database":
        return ObservationService(
            DatabaseObservationSessionRepository(session),
            DatabaseAgentActionLogRepository(session),
            DatabaseExternalImportRepository(session),
            report_service,
            timeline_service,
            profile_service,
            knowledge_service,
        )
    return ObservationService(
        ObservationSessionRepository(store),
        AgentActionLogRepository(store),
        ExternalImportRepository(store),
        report_service,
        timeline_service,
        profile_service,
        knowledge_service,
    )

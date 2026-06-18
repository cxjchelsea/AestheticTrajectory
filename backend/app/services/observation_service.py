from app.agent.observation_agent import ObservationAgentService
from app.repositories.agent_repository import AgentActionLogRepository, ObservationSessionRepository
from app.repositories.external_import_repository import ExternalImportRepository
from app.schemas.agent import AgentActionListResponse, CreateObservationRequest, ObservationSession
from app.schemas.external_context import CreateExternalImportRequest, ExternalImportBatch, ExternalImportListResponse
from app.services.knowledge_graph_query import KnowledgeGraphQueryService
from app.services.profile_service import ProfileService
from app.services.report_service import ReportService
from app.services.timeline_service import TimelineService
from app.agent.tool_registry import ToolContext


class ObservationService:
    def __init__(
        self,
        session_repository: ObservationSessionRepository,
        action_repository: AgentActionLogRepository,
        external_import_repository: ExternalImportRepository,
        report_service: ReportService,
        timeline_service: TimelineService,
        profile_service: ProfileService,
        knowledge_service: KnowledgeGraphQueryService,
    ) -> None:
        tool_context = ToolContext(
            report_service=report_service,
            timeline_service=timeline_service,
            profile_service=profile_service,
            knowledge_service=knowledge_service,
            external_import_repository=external_import_repository,
        )
        self.agent = ObservationAgentService(
            session_repository,
            action_repository,
            tool_context,
        )
        self.session_repository = session_repository
        self.action_repository = action_repository
        self.external_import_repository = external_import_repository

    def create_observation(self, user_id: str, request: CreateObservationRequest) -> ObservationSession:
        return self.agent.run_observation(user_id, request)

    def get_observation(self, user_id: str, session_id: str) -> ObservationSession | None:
        return self.session_repository.get_for_user(user_id, session_id)

    def list_agent_actions(
        self,
        user_id: str,
        *,
        session_id: str | None = None,
        limit: int = 100,
    ) -> AgentActionListResponse:
        return self.action_repository.list_by_user(user_id, session_id=session_id, limit=limit)

    def create_external_import(self, user_id: str, request: CreateExternalImportRequest) -> ExternalImportBatch:
        return self.external_import_repository.create_batch(user_id, request)

    def list_external_imports(self, user_id: str) -> ExternalImportListResponse:
        return self.external_import_repository.list_batches(user_id)

    def confirm_external_import(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        return self.external_import_repository.confirm_batch(user_id, batch_id)

    def reject_external_import(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        return self.external_import_repository.reject_batch(user_id, batch_id)

    def get_external_import(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        return self.external_import_repository.get_batch(user_id, batch_id)

from app.repositories.agent_repository import AgentActionLogRepository, ObservationSessionRepository
from app.repositories.external_import_repository import ExternalImportRepository
from app.repositories.memory_store import MemoryStore
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.agent import CreateObservationRequest
from app.schemas.external_context import CreateExternalImportRequest, ExternalContextItemDraft
from app.services.knowledge_graph_query import KnowledgeGraphQueryService
from app.services.observation_service import ObservationService
from app.services.profile_service import ProfileService
from app.services.report_service import ReportService
from app.services.timeline_service import TimelineService
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence, run_mock_aesthetic_analysis
from app.repositories.analysis_job_repository import AnalysisJobRepository
from app.repositories.input_repository import InputRepository
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import utc_now
from app.schemas.input import AestheticInputResponse


def _observation_service(store: MemoryStore) -> ObservationService:
    persistence = memory_workflow_persistence(store)
    report_service = ReportService(persistence.report_repository)
    timeline_service = TimelineService(
        persistence.timeline_repository,
        persistence.report_repository,
    )
    profile_service = ProfileService(ProfileRepository(store), persistence.timeline_repository)
    knowledge_service = KnowledgeGraphQueryService(KnowledgeGraphRepository())
    return ObservationService(
        ObservationSessionRepository(store),
        AgentActionLogRepository(store),
        ExternalImportRepository(store),
        report_service,
        timeline_service,
        profile_service,
        knowledge_service,
    )


def test_observation_abstains_without_reports() -> None:
    store = MemoryStore()
    service = _observation_service(store)

    session = service.create_observation(
        "user_anonymous",
        CreateObservationRequest(triggerSource="test", period="week"),
    )

    assert session.status == "abstained"
    assert session.message
    assert not session.summary
    actions = service.list_agent_actions("user_anonymous", session_id=session.id)
    assert actions.actions
    assert actions.actions[0].tool_name == "list_reports"


def test_observation_generates_summary_with_reports() -> None:
    store = MemoryStore()
    _run_workflow(store)
    service = _observation_service(store)

    session = service.create_observation(
        "user_anonymous",
        CreateObservationRequest(triggerSource="profile_page", period="week"),
    )

    assert session.status == "completed"
    assert session.summary
    assert session.evidence_refs
    assert any(ref.startswith("report_") for ref in session.evidence_refs)
    actions = service.list_agent_actions("user_anonymous", session_id=session.id)
    tool_names = {action.tool_name for action in actions.actions}
    assert "list_reports" in tool_names
    assert "get_report" in tool_names
    for action in actions.actions:
        assert action.reason
        assert action.status == "success"


def test_external_import_requires_confirmation() -> None:
    store = MemoryStore()
    service = _observation_service(store)

    batch = service.create_external_import(
        "user_anonymous",
        CreateExternalImportRequest(
            sourceSystem="mock_bookmarks",
            items=[
                ExternalContextItemDraft(
                    title="收藏：留白摄影",
                    snippet="外部收藏条目，只作补充上下文。",
                    sourceUri="https://example.com/item/1",
                    tags=["external", "photography"],
                )
            ],
        ),
    )
    assert batch.status == "pending_confirmation"

    confirmed = service.confirm_external_import("user_anonymous", batch.id)
    assert confirmed is not None
    assert confirmed.status == "confirmed"

    _run_workflow(store)
    session = service.create_observation(
        "user_anonymous",
        CreateObservationRequest(triggerSource="profile_page", period="week"),
    )
    assert session.status == "completed"
    assert any(ref.startswith("external_ctx_") for ref in session.evidence_refs)


def _run_workflow(store: MemoryStore, user_id: str = "user_anonymous") -> None:
    persistence = memory_workflow_persistence(store)
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id=f"input_{index}",
            userId=user_id,
            type="text",
            contentText=f"sample input {index}",
            fileUrl=None,
            source="test",
            title=f"Input {index}",
            description=None,
            createdAt=now,
        )
        for index in range(1, 4)
    ]
    for item in inputs:
        InputRepository(store).save(item)
    job = AnalysisJobResponse(
        id="job_observation_test",
        userId=user_id,
        status="created",
        inputCount=3,
        errorMessage=None,
        reportId=None,
        createdAt=utc_now(),
        startedAt=utc_now(),
        finishedAt=None,
    )
    AnalysisJobRepository(store).save(job)
    run_mock_aesthetic_analysis(job, inputs, persistence)

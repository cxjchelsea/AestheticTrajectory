from app.repositories.agent_repository import AgentActionLogRepository, ObservationSessionRepository
from app.repositories.external_import_repository import ExternalImportRepository
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.repositories.memory_store import MemoryStore
from app.repositories.profile_repository import ProfileRepository
from app.schemas.agent import CreateObservationRequest
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.common import utc_now
from app.schemas.input import AestheticInputResponse
from app.services.failure_replay import build_failure_replay
from app.services.grouping_stability import build_grouping_stability
from app.services.knowledge_graph_query import KnowledgeGraphQueryService
from app.services.observation_service import ObservationService
from app.services.profile_builder import build_profile_from_sources
from app.services.profile_service import ProfileService
from app.services.report_service import ReportService
from app.services.timeline_service import TimelineService
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence, run_mock_aesthetic_analysis


DIAGNOSTIC_TERMS = ("人格", "心理", "能力", "命运", "灵魂", "你一定", "消费规训")


def test_v4e_grouping_stability_does_not_feed_profile() -> None:
    store = MemoryStore()
    report_id, inputs = _run_workflow(store)
    report = store.reports[report_id]
    stability = build_grouping_stability(report, inputs)

    profile = build_profile_from_sources("user_anonymous", [report], [])
    positive_evidence_ids = {
        evidence.evidence_id
        for item in (profile.profile.items if profile.profile else [])
        if item.status in {"stable", "recent"} and item.weight > 0
        for evidence in item.evidence
    }

    assert stability.score == 1.0
    assert report.report_id not in positive_evidence_ids
    assert all(term not in stability.disclaimer for term in DIAGNOSTIC_TERMS[:4])


def test_v4e_failure_replay_does_not_hide_failed_step() -> None:
    now = utc_now()
    logs = [
        AnalysisLogRecord(
            id="log_failed",
            jobId="job_v4e_failed",
            stepId="cluster_inputs",
            status="failed",
            modelName=None,
            promptVersion=None,
            latencyMs=3,
            errorType="RuntimeError",
            errorMessage="clustering failed in test fixture",
            startedAt=now,
            finishedAt=now,
            createdAt=now,
        )
    ]
    replay = build_failure_replay("job_v4e_failed", "failed", logs, [])

    assert replay.failed is True
    assert replay.steps[0].status == "failed"
    assert replay.steps[0].error_message == "clustering failed in test fixture"
    assert all(term not in replay.replay_disclaimer for term in DIAGNOSTIC_TERMS)


def test_v4e_agent_and_knowledge_still_excluded_from_profile() -> None:
    store = MemoryStore()
    _run_workflow(store)
    observation_service = _observation_service(store)
    session = observation_service.create_observation(
        "user_anonymous",
        CreateObservationRequest(triggerSource="v4e_governance", period="week"),
    )
    assert session.status == "completed"

    reports = list(store.reports.values())
    profile = build_profile_from_sources("user_anonymous", reports, list(store.feedback.values()))
    positive_evidence_ids = {
        evidence.evidence_id
        for item in (profile.profile.items if profile.profile else [])
        if item.status in {"stable", "recent"} and item.weight > 0
        for evidence in item.evidence
    }

    for report in reports:
        if report.knowledge_context is not None:
            for item in report.knowledge_context.items:
                for ref in item.source_refs:
                    assert ref not in positive_evidence_ids
    assert session.id not in positive_evidence_ids


def _run_workflow(store: MemoryStore) -> tuple[str, list[AestheticInputResponse]]:
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id=f"input_v4e_{index}",
            userId="user_anonymous",
            type="text",
            contentText=f"quiet sample {index}",
            fileUrl=None,
            source="test",
            title=f"Quiet {index}",
            description="low density",
            createdAt=now,
        )
        for index in range(3)
    ]
    for item in inputs:
        store.inputs[item.id] = item
    job = AnalysisJobResponse(
        id="job_v4e",
        userId="user_anonymous",
        status="created",
        inputCount=3,
        errorMessage=None,
        reportId=None,
        createdAt=now,
        startedAt=now,
        finishedAt=None,
    )
    result = run_mock_aesthetic_analysis(job, inputs, memory_workflow_persistence(store))
    return result.report_id, inputs


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

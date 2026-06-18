from app.repositories.memory_store import MemoryStore
from app.schemas.agent import CreateObservationRequest
from app.services.profile_builder import build_profile_from_sources
from app.tests.unit.test_observation_agent import _observation_service, _run_workflow


def test_v4d_observation_summary_does_not_feed_profile_positive_evidence() -> None:
    store = MemoryStore()
    _run_workflow(store)
    service = _observation_service(store)

    session = service.create_observation(
        "user_anonymous",
        CreateObservationRequest(triggerSource="governance_test", period="week"),
    )
    assert session.status == "completed"
    assert session.evidence_refs

    reports = list(store.reports.values())
    profile = build_profile_from_sources("user_anonymous", reports, list(store.feedback.values()))

    positive_evidence_ids = {
        evidence.evidence_id
        for item in (profile.profile.items if profile.profile else [])
        if item.status in {"stable", "recent"} and item.weight > 0
        for evidence in item.evidence
    }
    for ref in session.evidence_refs:
        if ref.startswith("external_ctx_"):
            assert ref not in positive_evidence_ids
    assert session.id not in positive_evidence_ids

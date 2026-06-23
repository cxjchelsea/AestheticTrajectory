import pytest

from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.knowledge_context import AestheticKnowledgeContext, KnowledgeRetrievalMeta
from app.schemas.report import ReportResponse


def _feature() -> InputFeature:
    return InputFeature(
        inputId="input_1",
        featureType="image",
        lowLevelFeatures={
            "saturation": FeatureSignal(
                value="low",
                confidence=0.8,
                evidence=["low saturation evidence"],
            )
        },
        sampleEvidence=["low saturation image"],
        promptVersion="test",
        modelName="mock",
    )


def _report_with_failed_knowledge_vector() -> ReportResponse:
    return ReportResponse(
        reportId="report_1",
        title="title",
        summary="summary",
        lowLevelFeatures=[],
        similarityGroups=[],
        possibleInterpretations=[],
        insights=[],
        disclaimer="disclaimer",
        knowledgeContext=AestheticKnowledgeContext(
            disclaimer="d",
            retrievalMeta=KnowledgeRetrievalMeta(
                tagMatchCount=1,
                graphHitCount=0,
                vectorPath="failed",
                vectorErrorMessage="chroma unavailable",
            ),
        ),
    )


def test_knowledge_vector_query_failure_degrades_to_tag_matches(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.services.aesthetic_knowledge_retrieval as retrieval_module

    class FailingKnowledgeVectorStore:
        def query(self, vector, *, limit):
            raise RuntimeError("chroma unavailable")

    monkeypatch.setattr(retrieval_module, "settings_chroma_enabled", lambda: True)

    context = retrieval_module.build_aesthetic_knowledge_context(
        [_feature()],
        knowledge_vector_store=FailingKnowledgeVectorStore(),
    )

    assert context.items
    assert context.retrieval_meta is not None
    assert context.retrieval_meta.vector_path == "failed"
    assert context.retrieval_meta.vector_error_message == "chroma unavailable"


def test_knowledge_vector_store_init_failure_degrades_to_tag_matches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.workflows.steps.retrieve_aesthetic_knowledge as step_module

    def fail_get_store():
        raise RuntimeError("chroma client init failed")

    monkeypatch.setattr(step_module, "get_knowledge_vector_store", fail_get_store)

    context = step_module.retrieve_aesthetic_knowledge([_feature()])

    assert context.items
    assert context.retrieval_meta is not None
    assert context.retrieval_meta.vector_path == "failed"
    assert context.retrieval_meta.vector_error_message == "chroma client init failed"


def test_knowledge_vector_failure_creates_debug_fallback_event() -> None:
    import app.services.analysis_job_service as service_module

    events = service_module._knowledge_fallback_events(
        "job_1",
        _report_with_failed_knowledge_vector(),
    )

    assert len(events) == 1
    assert events[0].step_id == "retrieve_aesthetic_knowledge"
    assert events[0].fallback_type == "knowledge_vector_retrieval_failed"
    assert events[0].severity == "warning"
    assert "tag" in events[0].fallback_action

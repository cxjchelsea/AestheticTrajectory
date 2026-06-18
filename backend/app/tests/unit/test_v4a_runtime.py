import pytest

from app.repositories.chroma_debug_store import chroma_write_results
from app.repositories.memory_store import MemoryStore
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import utc_now
from app.schemas.input import AestheticInputResponse
from app.vector_store.input_vector_store import ChromaWriteResult, FakeInputVectorStore, reset_fake_input_vector_store
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence, run_mock_aesthetic_analysis


def test_workflow_records_chroma_skip_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHROMA_ENABLED", "false")

    from importlib import reload

    import app.core.config as config_module

    reload(config_module)

    store = MemoryStore()
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id="input_music",
            userId="user_anonymous",
            type="music",
            contentText=None,
            fileUrl="https://example.com/track",
            source="test",
            title="ambient track",
            description="metadata only",
            createdAt=now,
        ),
        AestheticInputResponse(
            id="input_video",
            userId="user_anonymous",
            type="video",
            contentText=None,
            fileUrl="https://example.com/clip",
            source="test",
            title="slow clip",
            description="metadata only",
            createdAt=now,
        ),
        AestheticInputResponse(
            id="input_text",
            userId="user_anonymous",
            type="text",
            contentText="quiet observation",
            fileUrl=None,
            source="test",
            title="note",
            description=None,
            createdAt=now,
        ),
    ]
    job = AnalysisJobResponse(
        id="job_multimodal",
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

    assert result.status == "completed"
    assert chroma_write_results[job.id].status == "skipped"
    assert store.embedding_records


def test_write_vectors_upserts_to_fake_store_when_chroma_enabled(monkeypatch) -> None:
    reset_fake_input_vector_store()
    fake_store = FakeInputVectorStore()

    monkeypatch.setenv("CHROMA_ENABLED", "true")
    monkeypatch.setenv("EMBEDDING_RUNTIME", "mock")

    from importlib import reload

    import app.core.config as config_module

    reload(config_module)

    import app.workflows.steps.write_vectors as write_vectors_module

    reload(write_vectors_module)
    monkeypatch.setattr(write_vectors_module, "get_input_vector_store", lambda: fake_store)

    now = utc_now()
    job = AnalysisJobResponse(
        id="job_chroma",
        userId="user_anonymous",
        status="created",
        inputCount=1,
        errorMessage=None,
        reportId=None,
        createdAt=now,
        startedAt=now,
        finishedAt=None,
    )
    input_record = AestheticInputResponse(
        id="input_text",
        userId="user_anonymous",
        type="text",
        contentText="sample",
        fileUrl=None,
        source="test",
        title="sample",
        description=None,
        createdAt=now,
    )
    embeddings = {"input_text": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]}

    records, chroma_result = write_vectors_module.write_vectors(
        job,
        [input_record],
        embeddings,
        embedding_texts={"input_text": "标题：sample\n正文：sample"},
    )

    assert len(records) == 1
    assert chroma_result.status == "success"
    assert chroma_result.upserted_count == 1
    assert fake_store.records


def test_chroma_success_boundary_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CHROMA_ENABLED", "true")

    from importlib import reload

    import app.core.config as config_module
    import app.services.analysis_job_service as analysis_job_service_module

    reload(config_module)
    reload(analysis_job_service_module)

    status, message = analysis_job_service_module._chroma_boundary_status(
        ChromaWriteResult(
            status="success",
            collection_name="inputs_mock_8",
            upserted_count=3,
        )
    )

    assert status == "dev_only"
    assert "inputs_mock_8" in message
    assert "3" in message

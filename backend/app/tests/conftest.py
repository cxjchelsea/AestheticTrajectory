import importlib

import pytest


@pytest.fixture(autouse=True)
def _reset_chroma_debug_store() -> None:
    from app.repositories.chroma_debug_store import chroma_write_results

    chroma_write_results.clear()
    yield
    chroma_write_results.clear()


@pytest.fixture(autouse=True)
def _reset_embedding_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_RUNTIME", "mock")
    monkeypatch.setenv("CHROMA_ENABLED", "false")
    monkeypatch.setenv("AUTH_MODE", "dev")
    monkeypatch.setenv("REPORT_LLM_RUNTIME", "mock")
    monkeypatch.setenv("IMAGE_FEATURE_RUNTIME", "mock")
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "metadata_only")
    monkeypatch.setenv("EXTERNAL_SOURCE_RUNTIME", "disabled")
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    import app.core.config as config_module
    import app.vector_store.chroma_client as chroma_client_module
    import app.vector_store.knowledge_vector_store as knowledge_vector_store_module

    importlib.reload(config_module)
    importlib.reload(chroma_client_module)
    importlib.reload(knowledge_vector_store_module)

    for module_name in (
        "app.services.analysis_job_service",
        "app.api.deps",
        "app.workflows.steps.retrieve_aesthetic_knowledge",
        "app.workflows.steps.write_vectors",
    ):
        importlib.reload(importlib.import_module(module_name))

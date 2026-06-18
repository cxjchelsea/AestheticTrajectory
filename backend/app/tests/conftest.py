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
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    import app.core.config as config_module

    importlib.reload(config_module)

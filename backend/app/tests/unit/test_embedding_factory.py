import pytest

from app.ai.factory import get_embedding_client
from app.ai.mock.mock_embedding import MockEmbeddingClient


def test_get_embedding_client_defaults_to_mock() -> None:
    client = get_embedding_client()
    assert isinstance(client, MockEmbeddingClient)
    assert client.vector_dimension == 8


def test_openai_runtime_without_api_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_RUNTIME", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    from importlib import reload

    import app.core.config as config_module
    import app.ai.factory as factory_module

    reload(config_module)
    reload(factory_module)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        factory_module.get_embedding_client()


def test_ollama_runtime_returns_ollama_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_RUNTIME", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("EMBEDDING_MODEL", "nomic-embed-text")
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")

    from importlib import reload

    import app.core.config as config_module
    import app.ai.factory as factory_module
    import app.ai.ollama.ollama_embedding as ollama_module

    reload(config_module)
    reload(factory_module)
    reload(ollama_module)

    client = factory_module.get_embedding_client()
    assert isinstance(client, ollama_module.OllamaEmbeddingClient)
    assert client.model_name == "nomic-embed-text"
    assert client.vector_dimension == 768


def test_ollama_runtime_without_base_url_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_RUNTIME", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "")
    monkeypatch.setenv("LLM_BASE_URL", "")

    from importlib import reload

    import app.core.config as config_module
    import app.ai.factory as factory_module

    reload(config_module)
    reload(factory_module)

    with pytest.raises(ValueError, match="OLLAMA_BASE_URL or LLM_BASE_URL is required"):
        factory_module.get_embedding_client()

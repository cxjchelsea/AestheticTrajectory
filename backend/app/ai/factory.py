from app.ai.embedding_client import EmbeddingClient
from app.ai.mock.mock_embedding import MockEmbeddingClient


def get_embedding_client() -> EmbeddingClient:
    from app.core.config import settings

    if settings.embedding_runtime == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_RUNTIME=openai")
        from app.ai.openai.openai_embedding import OpenAIEmbeddingClient

        return OpenAIEmbeddingClient(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model,
            vector_dimension=settings.embedding_dimensions,
        )
    if settings.embedding_runtime == "ollama":
        if not settings.ollama_base_url.strip():
            raise ValueError("OLLAMA_BASE_URL or LLM_BASE_URL is required when EMBEDDING_RUNTIME=ollama")
        from app.ai.ollama.ollama_embedding import OllamaEmbeddingClient

        return OllamaEmbeddingClient(
            base_url=settings.ollama_base_url,
            model_name=settings.embedding_model,
            vector_dimension=settings.embedding_dimensions,
        )
    return MockEmbeddingClient()

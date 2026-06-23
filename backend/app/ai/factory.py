from app.ai.embedding_client import EmbeddingClient
from app.ai.feature_extractor import FeatureExtractor
from app.ai.interpretation_generator import InterpretationGenerator
from app.ai.mock.mock_embedding import MockEmbeddingClient
from app.ai.mock.mock_feature_extractor import MockFeatureExtractor
from app.ai.mock.mock_interpretation_generator import MockInterpretationGenerator
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


class ModalityFeatureExtractor:
    model_name = "modality-feature-extractor-v6a"

    def __init__(self, *, fallback_extractor: FeatureExtractor, image_extractor: FeatureExtractor) -> None:
        self.fallback_extractor = fallback_extractor
        self.image_extractor = image_extractor

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        if input_record.type == "image":
            return self.image_extractor.extract(input_record, index)
        return self.fallback_extractor.extract(input_record, index)


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


def get_feature_extractor() -> FeatureExtractor:
    from app.core.config import settings

    runtime = settings.image_feature_runtime
    if runtime == "disabled":
        from app.ai.image_feature_extractor import DisabledImageFeatureExtractor

        image_extractor = DisabledImageFeatureExtractor()
    elif runtime == "ollama_vision":
        if not settings.ollama_base_url.strip():
            raise ValueError("OLLAMA_BASE_URL or LLM_BASE_URL is required when IMAGE_FEATURE_RUNTIME=ollama_vision")
        from app.ai.image_feature_extractor import OllamaVisionImageFeatureExtractor

        image_extractor = OllamaVisionImageFeatureExtractor(
            base_url=settings.ollama_base_url,
            model_name=settings.image_feature_model,
            timeout_seconds=settings.image_feature_timeout_seconds,
        )
    elif runtime == "mock":
        from app.ai.image_feature_extractor import MockImageFeatureExtractor

        image_extractor = MockImageFeatureExtractor()
    else:
        raise ValueError(f"Unsupported IMAGE_FEATURE_RUNTIME={runtime}")

    return ModalityFeatureExtractor(
        fallback_extractor=MockFeatureExtractor(),
        image_extractor=image_extractor,
    )


def get_interpretation_generator() -> InterpretationGenerator:
    from app.core.config import settings

    runtime = settings.report_llm_runtime
    if runtime == "ollama":
        if not settings.ollama_base_url.strip():
            raise ValueError("OLLAMA_BASE_URL or LLM_BASE_URL is required when REPORT_LLM_RUNTIME=ollama")
        from app.ai.ollama.ollama_interpretation_generator import OllamaInterpretationGenerator

        return OllamaInterpretationGenerator(
            base_url=settings.ollama_base_url,
            model_name=settings.report_llm_model,
            timeout_seconds=settings.report_llm_timeout_seconds,
        )
    if runtime == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when REPORT_LLM_RUNTIME=openai")
        raise ValueError("REPORT_LLM_RUNTIME=openai is not implemented in V5-B; use ollama or mock")
    return MockInterpretationGenerator()

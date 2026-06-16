from app.ai.embedding_client import EmbeddingClient
from app.ai.mock.mock_embedding import MockEmbeddingClient
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse
from app.workflows.steps.build_embedding_text import build_embedding_text


def generate_embeddings(
    inputs: list[AestheticInputResponse],
    features: list[InputFeature] | None = None,
    client: EmbeddingClient | None = None,
) -> dict[str, list[float]]:
    active_client = client or MockEmbeddingClient()
    feature_by_input_id = {feature.input_id: feature for feature in features or []}
    embeddings: dict[str, list[float]] = {}

    for input_record in inputs:
        embedding_text = build_embedding_text(input_record, feature_by_input_id.get(input_record.id))
        if not embedding_text:
            continue

        vector = active_client.embed(embedding_text)
        if len(vector) != active_client.vector_dimension:
            raise ValueError("Embedding vector dimension does not match client vector_dimension")
        embeddings[input_record.id] = vector

    return embeddings

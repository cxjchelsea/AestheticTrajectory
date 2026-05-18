from app.ai.mock.mock_embedding import MockEmbeddingClient
from app.schemas.input import AestheticInputResponse


def generate_embeddings(inputs: list[AestheticInputResponse]) -> dict[str, list[float]]:
    client = MockEmbeddingClient()
    return {
        input_record.id: client.embed(input_record.content_text or input_record.description or input_record.title or input_record.id)
        for input_record in inputs
    }

from app.ai.embedding_client import EmbeddingClient
from app.core.config import settings


INPUTS_COLLECTION = "inputs"


def input_collection_name(client: EmbeddingClient) -> str:
    runtime = settings.embedding_runtime
    return f"{settings.chroma_collection_inputs}_{runtime}_{client.vector_dimension}"

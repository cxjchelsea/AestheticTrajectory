from app.ai.embedding_client import EmbeddingClient
from app.ai.mock.mock_embedding import MockEmbeddingClient
from app.core.config import settings
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import new_id, utc_now
from app.schemas.embedding import EmbeddingRecord
from app.schemas.input import AestheticInputResponse


def write_vectors(
    job: AnalysisJobResponse,
    inputs: list[AestheticInputResponse],
    embeddings: dict[str, list[float]],
    client: EmbeddingClient | None = None,
) -> list[EmbeddingRecord]:
    active_client = client or MockEmbeddingClient()
    return [
        EmbeddingRecord(
            id=new_id("embedding"),
            ownerType="input",
            ownerId=input_record.id,
            collectionName=settings.chroma_collection_inputs,
            chromaId=f"chroma_{job.id}_{input_record.id}",
            modelName=active_client.model_name,
            vectorDimension=len(embeddings[input_record.id]),
            createdAt=utc_now(),
        )
        for input_record in inputs
        if input_record.id in embeddings
    ]

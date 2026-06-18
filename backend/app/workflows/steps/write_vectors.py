from app.ai.embedding_client import EmbeddingClient
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import new_id, utc_now
from app.schemas.embedding import EmbeddingRecord
from app.schemas.input import AestheticInputResponse
from app.vector_store.chroma_client import get_input_vector_store
from app.vector_store.collections import input_collection_name
from app.vector_store.input_vector_store import ChromaWriteResult, InputVectorMetadata


def write_vectors(
    job: AnalysisJobResponse,
    inputs: list[AestheticInputResponse],
    embeddings: dict[str, list[float]],
    client: EmbeddingClient | None = None,
    embedding_texts: dict[str, str] | None = None,
) -> tuple[list[EmbeddingRecord], ChromaWriteResult]:
    from app.ai.factory import get_embedding_client
    from app.core.config import settings

    active_client = client or get_embedding_client()
    collection_name = input_collection_name(active_client)
    records = [
        EmbeddingRecord(
            id=new_id("embedding"),
            ownerType="input",
            ownerId=input_record.id,
            collectionName=collection_name,
            chromaId=f"chroma_{job.id}_{input_record.id}",
            modelName=active_client.model_name,
            vectorDimension=len(embeddings[input_record.id]),
            createdAt=utc_now(),
        )
        for input_record in inputs
        if input_record.id in embeddings
    ]

    if not records:
        return records, ChromaWriteResult(status="skipped", message="No embeddings to write")

    if not settings.chroma_enabled:
        return records, ChromaWriteResult(
            status="skipped",
            message="CHROMA_ENABLED=false; embedding metadata saved without remote vector upsert",
            collection_name=collection_name,
        )

    try:
        store = get_input_vector_store()
        for record in records:
            input_record = next(item for item in inputs if item.id == record.owner_id)
            document = (embedding_texts or {}).get(record.owner_id, input_record.title or record.owner_id)
            metadata = InputVectorMetadata(
                inputId=record.owner_id,
                userId=job.user_id,
                jobId=job.id,
                inputType=input_record.type,
                modelName=record.model_name,
                vectorDimension=record.vector_dimension,
            )
            store.upsert(
                collection_name,
                record.chroma_id,
                embeddings[record.owner_id],
                metadata,
                document,
            )
        return records, ChromaWriteResult(
            status="success",
            message="Input vectors upserted to ChromaDB",
            collection_name=collection_name,
            upserted_count=len(records),
        )
    except Exception as exc:
        return records, ChromaWriteResult(
            status="failed",
            message=str(exc),
            collection_name=collection_name,
        )

from app.core.config import settings
from app.vector_store.input_vector_store import FakeInputVectorStore, InputVectorStore, get_fake_input_vector_store

_chroma_store: InputVectorStore | None = None


class ChromaInputVectorStore:
    def __init__(self, host: str, port: int) -> None:
        import chromadb

        self._client = chromadb.HttpClient(host=host, port=port)

    def upsert(
        self,
        collection_name: str,
        chroma_id: str,
        embedding: list[float],
        metadata,
        document: str,
    ) -> None:
        collection = self._client.get_or_create_collection(name=collection_name)
        collection.upsert(
            ids=[chroma_id],
            embeddings=[embedding],
            metadatas=[metadata.to_chroma_metadata()],
            documents=[document],
        )

    def query(
        self,
        collection_name: str,
        embedding: list[float],
        limit: int = 5,
    ) -> list[str]:
        collection = self._client.get_or_create_collection(name=collection_name)
        result = collection.query(query_embeddings=[embedding], n_results=limit)
        ids = result.get("ids") or []
        if not ids:
            return []
        return list(ids[0])


def get_input_vector_store() -> InputVectorStore:
    if settings.repository_backend == "memory" and not settings.chroma_enabled:
        return get_fake_input_vector_store()

    global _chroma_store
    if _chroma_store is None:
        if settings.chroma_enabled:
            _chroma_store = ChromaInputVectorStore(settings.chroma_host, settings.chroma_port)
        else:
            _chroma_store = get_fake_input_vector_store()
    return _chroma_store


def use_fake_input_vector_store_for_tests() -> FakeInputVectorStore:
    global _chroma_store
    fake = get_fake_input_vector_store()
    _chroma_store = fake
    return fake

from dataclasses import dataclass, field

from pydantic import BaseModel, Field

from app.ai.knowledge.aesthetic_knowledge_base import AESTHETIC_KNOWLEDGE_CHUNKS
from app.ai.knowledge.knowledge_graph_seed import CONCEPTS
from app.core.config import settings
from app.vector_store.chroma_client import get_input_vector_store


class KnowledgeVectorMetadata(BaseModel):
    doc_id: str = Field(alias="docId")
    concept_ids: list[str] = Field(default_factory=list, alias="conceptIds")
    feature_tags: list[str] = Field(default_factory=list, alias="featureTags")

    model_config = {"populate_by_name": True}

    def to_chroma_metadata(self) -> dict[str, str]:
        return {
            "docId": self.doc_id,
            "conceptIds": ",".join(self.concept_ids),
            "featureTags": ",".join(self.feature_tags),
        }


@dataclass
class KnowledgeVectorQueryResult:
    doc_ids: list[str]
    path: str


@dataclass
class FakeKnowledgeVectorStore:
    records: dict[str, dict[str, object]] = field(default_factory=dict)
    seeded: bool = False

    def ensure_seeded(self) -> None:
        if self.seeded:
            return
        for chunk in AESTHETIC_KNOWLEDGE_CHUNKS:
            concept_ids = [
                concept.id
                for concept in CONCEPTS
                if chunk.doc_id in concept.source_refs
            ]
            metadata = KnowledgeVectorMetadata(
                docId=chunk.doc_id,
                conceptIds=concept_ids,
                featureTags=sorted(chunk.feature_tags),
            )
            key = f"{_collection_name()}:{chunk.doc_id}"
            self.records[key] = {
                "metadata": metadata.to_chroma_metadata(),
                "document": f"{chunk.title}\n{chunk.snippet}",
            }
        self.seeded = True

    def query(self, embedding: list[float], *, limit: int = 3) -> KnowledgeVectorQueryResult:
        self.ensure_seeded()
        doc_ids = [
            str(record["metadata"]["docId"])
            for record in self.records.values()
            if "metadata" in record
        ]
        return KnowledgeVectorQueryResult(doc_ids=doc_ids[:limit], path="used")


def _collection_name() -> str:
    return f"{settings.chroma_collection_knowledge}_{settings.embedding_runtime}_{settings.embedding_dimensions}"


def _concept_ids_for_doc(doc_id: str) -> list[str]:
    return [concept.id for concept in CONCEPTS if doc_id in concept.source_refs]


class KnowledgeVectorStore:
    def __init__(self, vector_store) -> None:
        self.vector_store = vector_store
        self._seeded = False

    def ensure_seeded(self, embedding_client) -> None:
        if self._seeded or not settings.chroma_enabled:
            return
        collection_name = _collection_name()
        for chunk in AESTHETIC_KNOWLEDGE_CHUNKS:
            text = f"{chunk.title}\n{chunk.snippet}"
            vector = embedding_client.embed(text)
            metadata = KnowledgeVectorMetadata(
                docId=chunk.doc_id,
                conceptIds=_concept_ids_for_doc(chunk.doc_id),
                featureTags=sorted(chunk.feature_tags),
            )
            self.vector_store.upsert(
                collection_name=collection_name,
                chroma_id=chunk.doc_id,
                embedding=vector,
                metadata=metadata,
                document=text,
            )
        self._seeded = True

    def query(self, embedding: list[float], *, limit: int = 3) -> KnowledgeVectorQueryResult:
        if not settings.chroma_enabled:
            return KnowledgeVectorQueryResult(doc_ids=[], path="skipped")
        collection_name = _collection_name()
        doc_ids = self.vector_store.query(collection_name, embedding, limit=limit)
        return KnowledgeVectorQueryResult(doc_ids=doc_ids, path="used")


_fake_store: FakeKnowledgeVectorStore | None = None


def get_knowledge_vector_store() -> KnowledgeVectorStore | FakeKnowledgeVectorStore:
    global _fake_store
    if settings.repository_backend == "memory" and not settings.chroma_enabled:
        if _fake_store is None:
            _fake_store = FakeKnowledgeVectorStore()
        return _fake_store
    return KnowledgeVectorStore(get_input_vector_store())

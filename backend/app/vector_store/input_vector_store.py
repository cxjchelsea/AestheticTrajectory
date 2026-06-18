from dataclasses import dataclass, field
from typing import Protocol

from pydantic import BaseModel, Field


class InputVectorMetadata(BaseModel):
    input_id: str = Field(alias="inputId")
    user_id: str = Field(alias="userId")
    job_id: str = Field(alias="jobId")
    input_type: str = Field(alias="inputType")
    model_name: str = Field(alias="modelName")
    vector_dimension: int = Field(alias="vectorDimension")

    model_config = {"populate_by_name": True}

    def to_chroma_metadata(self) -> dict[str, str | int]:
        return {
            "inputId": self.input_id,
            "userId": self.user_id,
            "jobId": self.job_id,
            "inputType": self.input_type,
            "modelName": self.model_name,
            "vectorDimension": self.vector_dimension,
        }


@dataclass
class ChromaWriteResult:
    status: str
    message: str | None = None
    collection_name: str | None = None
    upserted_count: int = 0


class InputVectorStore(Protocol):
    def upsert(
        self,
        collection_name: str,
        chroma_id: str,
        embedding: list[float],
        metadata: InputVectorMetadata,
        document: str,
    ) -> None:
        ...

    def query(
        self,
        collection_name: str,
        embedding: list[float],
        limit: int = 5,
    ) -> list[str]:
        ...


@dataclass
class FakeInputVectorStore:
    records: dict[str, dict[str, object]] = field(default_factory=dict)

    def upsert(
        self,
        collection_name: str,
        chroma_id: str,
        embedding: list[float],
        metadata: InputVectorMetadata,
        document: str,
    ) -> None:
        key = f"{collection_name}:{chroma_id}"
        self.records[key] = {
            "embedding": embedding,
            "metadata": metadata.to_chroma_metadata(),
            "document": document,
        }

    def query(
        self,
        collection_name: str,
        embedding: list[float],
        limit: int = 5,
    ) -> list[str]:
        prefix = f"{collection_name}:"
        matches = [key.split(":", 1)[1] for key in self.records if key.startswith(prefix)]
        return matches[:limit]


_fake_store = FakeInputVectorStore()


def get_fake_input_vector_store() -> FakeInputVectorStore:
    return _fake_store


def reset_fake_input_vector_store() -> None:
    _fake_store.records.clear()

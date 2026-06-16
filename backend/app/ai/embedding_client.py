from typing import Protocol


class EmbeddingClient(Protocol):
    vector_dimension: int

    @property
    def model_name(self) -> str:
        ...

    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for non-empty semantic text."""
        ...

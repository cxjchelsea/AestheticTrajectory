from app.core.config import settings


class MockEmbeddingClient:
    vector_dimension = 8

    def embed(self, text: str) -> list[float]:
        seed = sum(ord(char) for char in text)
        return [((seed + index * 17) % 100) / 100 for index in range(self.vector_dimension)]

    @property
    def model_name(self) -> str:
        return settings.embedding_model

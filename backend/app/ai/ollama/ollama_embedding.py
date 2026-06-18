import json
from urllib import error, request

from app.ai.embedding_client import EmbeddingClient


class OllamaEmbeddingClient:
    def __init__(self, base_url: str, model_name: str, vector_dimension: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self.vector_dimension = vector_dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding input text must not be empty")

        payload = json.dumps(
            {
                "model": self._model_name,
                "input": text,
            }
        ).encode("utf-8")
        http_request = request.Request(
            f"{self._base_url}/api/embed",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"Ollama embedding request failed: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise ValueError(f"Ollama embedding request failed: {exc.reason}") from exc

        embeddings = body.get("embeddings")
        if not embeddings:
            raise ValueError("Ollama embedding response missing embeddings")
        embedding = embeddings[0]
        if len(embedding) != self.vector_dimension:
            raise ValueError(
                f"Ollama embedding dimension mismatch: expected {self.vector_dimension}, got {len(embedding)}"
            )
        return [float(value) for value in embedding]

    def health_url(self) -> str:
        return f"{self._base_url}/api/tags"

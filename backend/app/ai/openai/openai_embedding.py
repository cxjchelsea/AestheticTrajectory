import json
from urllib import error, request

from app.ai.embedding_client import EmbeddingClient


class OpenAIEmbeddingClient:
    def __init__(self, api_key: str, model_name: str, vector_dimension: int) -> None:
        self._api_key = api_key
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
                "dimensions": self.vector_dimension,
            }
        ).encode("utf-8")
        http_request = request.Request(
            "https://api.openai.com/v1/embeddings",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"OpenAI embedding request failed: {exc.code} {detail}") from exc
        except error.URLError as exc:
            raise ValueError(f"OpenAI embedding request failed: {exc.reason}") from exc

        embedding = body["data"][0]["embedding"]
        if len(embedding) != self.vector_dimension:
            raise ValueError(
                f"OpenAI embedding dimension mismatch: expected {self.vector_dimension}, got {len(embedding)}"
            )
        return [float(value) for value in embedding]

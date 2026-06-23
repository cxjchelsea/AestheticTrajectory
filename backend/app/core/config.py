from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = "Aesthetic Trajectory API"
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "mock-embedding-v1")
    embedding_runtime: str = os.getenv("EMBEDDING_RUNTIME", "mock")
    embedding_dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "512"))
    openai_api_key: str = os.getenv("OPENAI_API_KEY", os.getenv("LLM_API_KEY", ""))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434"))
    repository_backend: str = os.getenv("REPOSITORY_BACKEND", "memory")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://aesthetic:aesthetic@localhost:5432/aesthetic_trajectory",
    )
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    chroma_collection_inputs: str = "inputs"
    chroma_collection_knowledge: str = "knowledge"
    chroma_enabled: bool = os.getenv("CHROMA_ENABLED", "false").lower() in {"1", "true", "yes"}
    chroma_host: str = os.getenv("CHROMA_HOST", "127.0.0.1")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8001"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173")

    @property
    def auth_mode(self) -> str:
        return os.getenv("AUTH_MODE", "dev")

    @property
    def session_cookie_name(self) -> str:
        return os.getenv("SESSION_COOKIE_NAME", "aesthetic_session")

    @property
    def session_ttl_days(self) -> int:
        return int(os.getenv("SESSION_TTL_DAYS", "365"))

    @property
    def report_llm_runtime(self) -> str:
        return os.getenv("REPORT_LLM_RUNTIME", "mock")

    @property
    def report_llm_model(self) -> str:
        return os.getenv("REPORT_LLM_MODEL", "llama3.2")

    @property
    def report_llm_timeout_seconds(self) -> int:
        return int(os.getenv("REPORT_LLM_TIMEOUT_SECONDS", "120"))

    @property
    def external_source_runtime(self) -> str:
        return os.getenv("EXTERNAL_SOURCE_RUNTIME", "disabled")

    @property
    def external_source_provider(self) -> str:
        return os.getenv("EXTERNAL_SOURCE_PROVIDER", "demo_notes")

    @property
    def external_source_redirect_uri(self) -> str:
        return os.getenv("EXTERNAL_SOURCE_REDIRECT_URI", "")

    @property
    def external_source_required_scopes(self) -> list[str]:
        raw = os.getenv("EXTERNAL_SOURCE_REQUIRED_SCOPES", "read")
        return [scope.strip() for scope in raw.split(",") if scope.strip()]


settings = Settings()

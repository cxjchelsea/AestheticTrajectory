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
    repository_backend: str = os.getenv("REPOSITORY_BACKEND", "memory")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://aesthetic:aesthetic@localhost:5432/aesthetic_trajectory",
    )
    test_database_url: str = os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")
    chroma_collection_inputs: str = "inputs"
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173")


settings = Settings()

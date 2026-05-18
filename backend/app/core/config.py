from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "Aesthetic Trajectory API"
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "mock-embedding-v1")
    chroma_collection_inputs: str = "inputs"
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173")


settings = Settings()

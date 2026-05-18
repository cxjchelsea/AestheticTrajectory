from pathlib import Path

from app.core.config import settings


def upload_root() -> Path:
    return Path(settings.upload_dir)

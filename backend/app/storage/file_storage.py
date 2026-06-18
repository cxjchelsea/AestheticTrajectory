import mimetypes
import re
from pathlib import Path

from app.core.config import settings
from app.schemas.common import new_id, utc_now
from app.schemas.file import FileUploadResponse
from app.storage.local_storage import upload_root


ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def save_upload(file_name: str, content: bytes, mime_type: str | None, user_id: str = "user_anonymous") -> FileUploadResponse:
    if len(content) > settings.max_upload_bytes:
        raise ValueError(f"Upload exceeds MAX_UPLOAD_BYTES ({settings.max_upload_bytes})")

    resolved_mime = mime_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    if resolved_mime not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError(f"Unsupported image mime type: {resolved_mime}")

    extension = _safe_extension(file_name, resolved_mime)
    file_id = new_id("file")
    user_dir = upload_root() / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    target_path = user_dir / f"{file_id}{extension}"
    target_path.write_bytes(content)

    return FileUploadResponse(
        fileId=file_id,
        fileUrl=f"/api/files/{file_id}",
        mimeType=resolved_mime,
        sizeBytes=len(content),
        createdAt=utc_now(),
    )


def resolve_uploaded_file(file_id: str, user_id: str = "user_anonymous") -> Path | None:
    user_dir = upload_root() / user_id
    if not user_dir.exists():
        return None
    matches = list(user_dir.glob(f"{file_id}.*"))
    if not matches:
        return None
    return matches[0]


def _safe_extension(file_name: str, mime_type: str) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return suffix
    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return mapping.get(mime_type, ".bin")

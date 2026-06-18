from datetime import datetime

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    file_id: str = Field(alias="fileId")
    file_url: str = Field(alias="fileUrl")
    mime_type: str = Field(alias="mimeType")
    size_bytes: int = Field(alias="sizeBytes")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}

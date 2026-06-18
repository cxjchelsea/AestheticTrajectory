from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


InputType = Literal["image", "text", "music", "video"]


class CreateInputRequest(BaseModel):
    type: InputType
    content_text: str | None = Field(default=None, alias="contentText")
    file_url: str | None = Field(default=None, alias="fileUrl")
    source: str = "manual"
    title: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_metadata(self) -> "CreateInputRequest":
        if self.type == "text" and not (self.content_text and self.content_text.strip()):
            raise ValueError("text input requires contentText")
        if self.type in {"music", "video"} and not (
            (self.title and self.title.strip()) or (self.file_url and self.file_url.strip())
        ):
            raise ValueError(f"{self.type} input requires title or fileUrl")
        return self


class AestheticInputResponse(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    type: InputType
    content_text: str | None = Field(default=None, alias="contentText")
    file_url: str | None = Field(default=None, alias="fileUrl")
    source: str
    title: str | None
    description: str | None
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


InputType = Literal["image", "text"]


class CreateInputRequest(BaseModel):
    type: InputType
    content_text: str | None = Field(default=None, alias="contentText")
    file_url: str | None = Field(default=None, alias="fileUrl")
    source: str = "manual"
    title: str | None = None
    description: str | None = None


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

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EXTERNAL_CONTEXT_DISCLAIMER = (
    "外部导入内容只作为补充观察上下文，不代表用户偏好证据，需经用户确认后才会被引用。"
)

ExternalImportStatus = Literal["pending_confirmation", "confirmed", "rejected"]


class ExternalContextItemDraft(BaseModel):
    title: str
    snippet: str
    source_uri: str | None = Field(default=None, alias="sourceUri")
    tags: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class CreateExternalImportRequest(BaseModel):
    source_system: str = Field(alias="sourceSystem")
    items: list[ExternalContextItemDraft]

    model_config = {"populate_by_name": True}


class ExternalContextItem(BaseModel):
    id: str
    batch_id: str = Field(alias="batchId")
    user_id: str = Field(alias="userId")
    title: str
    snippet: str
    source_uri: str | None = Field(default=None, alias="sourceUri")
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}


class ExternalImportBatch(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    source_system: str = Field(alias="sourceSystem")
    status: ExternalImportStatus
    item_count: int = Field(alias="itemCount")
    items: list[ExternalContextItem] = Field(default_factory=list)
    confirmed_at: datetime | None = Field(default=None, alias="confirmedAt")
    created_at: datetime = Field(alias="createdAt")
    disclaimer: str = EXTERNAL_CONTEXT_DISCLAIMER

    model_config = {"populate_by_name": True}


class ExternalImportListResponse(BaseModel):
    user_id: str = Field(alias="userId")
    batches: list[ExternalImportBatch]
    total: int

    model_config = {"populate_by_name": True}

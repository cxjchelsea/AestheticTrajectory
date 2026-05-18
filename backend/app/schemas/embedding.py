from datetime import datetime

from pydantic import BaseModel, Field


class EmbeddingRecord(BaseModel):
    id: str
    owner_type: str = Field(alias="ownerType")
    owner_id: str = Field(alias="ownerId")
    collection_name: str = Field(alias="collectionName")
    chroma_id: str = Field(alias="chromaId")
    model_name: str = Field(alias="modelName")
    vector_dimension: int = Field(alias="vectorDimension")
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True}

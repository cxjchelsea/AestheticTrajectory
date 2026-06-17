from pydantic import BaseModel, Field


class HistoryContextItem(BaseModel):
    source_type: str = Field(alias="sourceType")
    source_id: str = Field(alias="sourceId")
    source_refs: list[str] = Field(alias="sourceRefs")
    direction: str
    matched_features: list[str] = Field(default_factory=list, alias="matchedFeatures")
    label: str
    note: str

    model_config = {"populate_by_name": True}


class PersonalHistoryContext(BaseModel):
    items: list[HistoryContextItem] = Field(default_factory=list)
    summary: str | None = None
    message: str | None = None
    disclaimer: str

    model_config = {"populate_by_name": True}

from pydantic import BaseModel, Field


class KnowledgeContextItem(BaseModel):
    doc_id: str = Field(alias="docId")
    title: str
    snippet: str
    matched_features: list[str] = Field(default_factory=list, alias="matchedFeatures")
    source_refs: list[str] = Field(alias="sourceRefs")
    note: str

    model_config = {"populate_by_name": True}


class AestheticKnowledgeContext(BaseModel):
    items: list[KnowledgeContextItem] = Field(default_factory=list)
    summary: str | None = None
    message: str | None = None
    disclaimer: str

    model_config = {"populate_by_name": True}

from typing import Literal

from pydantic import BaseModel, Field


class KnowledgeRetrievalMeta(BaseModel):
    tag_match_count: int = Field(alias="tagMatchCount")
    graph_hit_count: int = Field(alias="graphHitCount")
    vector_path: Literal["skipped", "used", "not_applicable"] = Field(alias="vectorPath")
    abstention_reason: str | None = Field(default=None, alias="abstentionReason")

    model_config = {"populate_by_name": True}


class KnowledgeContextItem(BaseModel):
    doc_id: str = Field(alias="docId")
    title: str
    snippet: str
    matched_features: list[str] = Field(default_factory=list, alias="matchedFeatures")
    source_refs: list[str] = Field(alias="sourceRefs")
    note: str
    related_concept_ids: list[str] = Field(default_factory=list, alias="relatedConceptIds")
    relation_notes: list[str] = Field(default_factory=list, alias="relationNotes")

    model_config = {"populate_by_name": True}


class AestheticKnowledgeContext(BaseModel):
    items: list[KnowledgeContextItem] = Field(default_factory=list)
    summary: str | None = None
    message: str | None = None
    disclaimer: str
    retrieval_meta: KnowledgeRetrievalMeta | None = Field(default=None, alias="retrievalMeta")

    model_config = {"populate_by_name": True}

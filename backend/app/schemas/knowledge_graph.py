from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ConceptPredicate = Literal["related_to", "contrasts_with", "example_of"]


class SourceEvidence(BaseModel):
    doc_ids: list[str] = Field(default_factory=list, alias="docIds")
    note: str

    model_config = {"populate_by_name": True}


class AestheticConcept(BaseModel):
    id: str
    slug: str
    label: str
    description: str
    feature_tags: list[str] = Field(default_factory=list, alias="featureTags")
    source_refs: list[str] = Field(default_factory=list, alias="sourceRefs")
    created_at: datetime | None = Field(default=None, alias="createdAt")

    model_config = {"populate_by_name": True}


class ConceptRelation(BaseModel):
    id: str
    from_concept_id: str = Field(alias="fromConceptId")
    to_concept_id: str = Field(alias="toConceptId")
    predicate: ConceptPredicate
    source_evidence: SourceEvidence = Field(alias="sourceEvidence")
    created_at: datetime | None = Field(default=None, alias="createdAt")

    model_config = {"populate_by_name": True}


class KnowledgeChunkSummary(BaseModel):
    doc_id: str = Field(alias="docId")
    title: str
    snippet: str
    feature_tags: list[str] = Field(default_factory=list, alias="featureTags")
    source: str

    model_config = {"populate_by_name": True}


class ConceptDetailResponse(BaseModel):
    concept: AestheticConcept
    outgoing: list[ConceptRelation] = Field(default_factory=list)
    incoming: list[ConceptRelation] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class GraphEdgeView(BaseModel):
    relation: ConceptRelation
    from_label: str = Field(alias="fromLabel")
    to_label: str = Field(alias="toLabel")

    model_config = {"populate_by_name": True}


class KnowledgeGraphResponse(BaseModel):
    root_concept_id: str = Field(alias="rootConceptId")
    concepts: list[AestheticConcept]
    edges: list[GraphEdgeView]
    disclaimer: str

    model_config = {"populate_by_name": True}


class ConceptListResponse(BaseModel):
    concepts: list[AestheticConcept]
    total: int

    model_config = {"populate_by_name": True}


class KnowledgeChunkListResponse(BaseModel):
    chunks: list[KnowledgeChunkSummary]
    total: int

    model_config = {"populate_by_name": True}

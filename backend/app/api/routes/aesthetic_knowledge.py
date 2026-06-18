from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_knowledge_graph_service
from app.schemas.knowledge_graph import (
    ConceptDetailResponse,
    ConceptListResponse,
    KnowledgeChunkListResponse,
    KnowledgeGraphResponse,
)
from app.services.knowledge_graph_query import KnowledgeGraphQueryService

router = APIRouter(tags=["aesthetic-knowledge"])


@router.get("/aesthetic-knowledge/concepts", response_model=ConceptListResponse)
def list_concepts(
    feature_tag: str | None = Query(default=None, alias="featureTag"),
    service: KnowledgeGraphQueryService = Depends(get_knowledge_graph_service),
) -> ConceptListResponse:
    return service.list_concepts(feature_tag=feature_tag)


@router.get("/aesthetic-knowledge/concepts/{concept_id}", response_model=ConceptDetailResponse)
def get_concept_detail(
    concept_id: str,
    service: KnowledgeGraphQueryService = Depends(get_knowledge_graph_service),
) -> ConceptDetailResponse:
    detail = service.get_concept_detail(concept_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return detail


@router.get("/aesthetic-knowledge/graph", response_model=KnowledgeGraphResponse)
def get_knowledge_graph(
    concept_id: str = Query(alias="conceptId"),
    service: KnowledgeGraphQueryService = Depends(get_knowledge_graph_service),
) -> KnowledgeGraphResponse:
    graph = service.get_one_hop_graph(concept_id)
    if graph is None:
        raise HTTPException(status_code=404, detail="Concept not found")
    return graph


@router.get("/aesthetic-knowledge/chunks", response_model=KnowledgeChunkListResponse)
def list_knowledge_chunks(
    service: KnowledgeGraphQueryService = Depends(get_knowledge_graph_service),
) -> KnowledgeChunkListResponse:
    return service.list_chunks()

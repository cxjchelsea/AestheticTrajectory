from app.ai.knowledge.knowledge_graph_seed import KNOWLEDGE_GRAPH_DISCLAIMER, knowledge_chunk_summaries
from app.schemas.knowledge_graph import (
    ConceptDetailResponse,
    ConceptListResponse,
    GraphEdgeView,
    KnowledgeChunkListResponse,
    KnowledgeGraphResponse,
)


PREDICATE_LABELS = {
    "related_to": "相关",
    "contrasts_with": "对比",
    "example_of": "示例",
}


class KnowledgeGraphQueryService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def list_concepts(self, *, feature_tag: str | None = None) -> ConceptListResponse:
        concepts = self.repository.list_concepts(feature_tag=feature_tag)
        return ConceptListResponse(concepts=concepts, total=len(concepts))

    def get_concept_detail(self, concept_id: str) -> ConceptDetailResponse | None:
        concept = self.repository.get_concept(concept_id)
        if concept is None:
            return None
        outgoing, incoming = self.repository.list_relations_for_concept(concept_id)
        return ConceptDetailResponse(concept=concept, outgoing=outgoing, incoming=incoming)

    def get_one_hop_graph(self, concept_id: str) -> KnowledgeGraphResponse | None:
        if self.repository.get_concept(concept_id) is None:
            return None

        concepts, edges = self.repository.expand_one_hop({concept_id})
        concept_by_id = {concept.id: concept for concept in concepts}
        edge_views: list[GraphEdgeView] = []
        for relation in edges:
            from_concept = concept_by_id.get(relation.from_concept_id)
            to_concept = concept_by_id.get(relation.to_concept_id)
            if from_concept is None or to_concept is None:
                continue
            edge_views.append(
                GraphEdgeView(
                    relation=relation,
                    fromLabel=from_concept.label,
                    toLabel=to_concept.label,
                )
            )

        return KnowledgeGraphResponse(
            rootConceptId=concept_id,
            concepts=concepts,
            edges=edge_views,
            disclaimer=KNOWLEDGE_GRAPH_DISCLAIMER,
        )

    def list_chunks(self) -> KnowledgeChunkListResponse:
        chunks = knowledge_chunk_summaries()
        return KnowledgeChunkListResponse(chunks=chunks, total=len(chunks))

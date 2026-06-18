from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.ai.knowledge.knowledge_graph_seed import CONCEPTS, RELATIONS
from app.models.persistence import AestheticConceptModel, AestheticConceptRelationModel
from app.schemas.knowledge_graph import AestheticConcept, ConceptRelation, SourceEvidence


def _concept_from_model(row: AestheticConceptModel) -> AestheticConcept:
    return AestheticConcept(
        id=row.id,
        slug=row.slug,
        label=row.label,
        description=row.description,
        featureTags=list(row.feature_tags_json or []),
        sourceRefs=list(row.source_refs_json or []),
        createdAt=row.created_at,
    )


def _relation_from_model(row: AestheticConceptRelationModel) -> ConceptRelation | None:
    evidence_raw = row.source_evidence_json or {}
    doc_ids = evidence_raw.get("docIds") or evidence_raw.get("doc_ids") or []
    note = evidence_raw.get("note") or ""
    if not doc_ids or not note:
        return None
    return ConceptRelation(
        id=row.id,
        fromConceptId=row.from_concept_id,
        toConceptId=row.to_concept_id,
        predicate=row.predicate,
        sourceEvidence=SourceEvidence(docIds=list(doc_ids), note=note),
        createdAt=row.created_at,
    )


class KnowledgeGraphRepository:
    def __init__(self) -> None:
        self._concepts = {concept.id: concept for concept in CONCEPTS}
        self._relations = [relation for relation in RELATIONS if relation.source_evidence.doc_ids]

    def list_concepts(self, *, feature_tag: str | None = None) -> list[AestheticConcept]:
        concepts = list(self._concepts.values())
        if feature_tag:
            concepts = [concept for concept in concepts if feature_tag in concept.feature_tags]
        return sorted(concepts, key=lambda item: item.slug)

    def get_concept(self, concept_id: str) -> AestheticConcept | None:
        return self._concepts.get(concept_id)

    def find_concepts_by_doc_id(self, doc_id: str) -> list[AestheticConcept]:
        return sorted(
            [concept for concept in self._concepts.values() if doc_id in concept.source_refs],
            key=lambda item: item.id,
        )

    def find_concepts_by_feature_tags(self, feature_tags: set[str]) -> list[AestheticConcept]:
        if not feature_tags:
            return []
        return sorted(
            [
                concept
                for concept in self._concepts.values()
                if feature_tags & set(concept.feature_tags)
            ],
            key=lambda item: item.id,
        )

    def list_relations_for_concept(self, concept_id: str) -> tuple[list[ConceptRelation], list[ConceptRelation]]:
        outgoing = [
            relation
            for relation in self._relations
            if relation.from_concept_id == concept_id
        ]
        incoming = [
            relation
            for relation in self._relations
            if relation.to_concept_id == concept_id
        ]
        return outgoing, incoming

    def expand_one_hop(self, concept_ids: set[str]) -> tuple[list[AestheticConcept], list[ConceptRelation]]:
        if not concept_ids:
            return [], []

        concepts: dict[str, AestheticConcept] = {}
        edges: list[ConceptRelation] = []
        seen_edge_ids: set[str] = set()

        for concept_id in concept_ids:
            concept = self.get_concept(concept_id)
            if concept is not None:
                concepts[concept.id] = concept

        for concept_id in concept_ids:
            outgoing, incoming = self.list_relations_for_concept(concept_id)
            for relation in outgoing + incoming:
                if relation.id in seen_edge_ids:
                    continue
                seen_edge_ids.add(relation.id)
                edges.append(relation)
                for related_id in (relation.from_concept_id, relation.to_concept_id):
                    related = self.get_concept(related_id)
                    if related is not None:
                        concepts[related.id] = related

        return list(concepts.values()), edges


class DatabaseKnowledgeGraphRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_concepts(self, *, feature_tag: str | None = None) -> list[AestheticConcept]:
        rows = self.session.scalars(
            select(AestheticConceptModel).order_by(AestheticConceptModel.slug.asc())
        ).all()
        concepts = [_concept_from_model(row) for row in rows]
        if feature_tag:
            concepts = [concept for concept in concepts if feature_tag in concept.feature_tags]
        return concepts

    def get_concept(self, concept_id: str) -> AestheticConcept | None:
        row = self.session.get(AestheticConceptModel, concept_id)
        return _concept_from_model(row) if row is not None else None

    def find_concepts_by_doc_id(self, doc_id: str) -> list[AestheticConcept]:
        rows = self.session.scalars(select(AestheticConceptModel)).all()
        return sorted(
            [
                _concept_from_model(row)
                for row in rows
                if doc_id in (row.source_refs_json or [])
            ],
            key=lambda item: item.id,
        )

    def find_concepts_by_feature_tags(self, feature_tags: set[str]) -> list[AestheticConcept]:
        if not feature_tags:
            return []
        rows = self.session.scalars(select(AestheticConceptModel)).all()
        matched: list[AestheticConcept] = []
        for row in rows:
            tags = set(row.feature_tags_json or [])
            if feature_tags & tags:
                matched.append(_concept_from_model(row))
        return sorted(matched, key=lambda item: item.id)

    def list_relations_for_concept(self, concept_id: str) -> tuple[list[ConceptRelation], list[ConceptRelation]]:
        rows = self.session.scalars(select(AestheticConceptRelationModel)).all()
        outgoing: list[ConceptRelation] = []
        incoming: list[ConceptRelation] = []
        for row in rows:
            relation = _relation_from_model(row)
            if relation is None:
                continue
            if row.from_concept_id == concept_id:
                outgoing.append(relation)
            if row.to_concept_id == concept_id:
                incoming.append(relation)
        return outgoing, incoming

    def expand_one_hop(self, concept_ids: set[str]) -> tuple[list[AestheticConcept], list[ConceptRelation]]:
        if not concept_ids:
            return [], []

        rows = self.session.scalars(
            select(AestheticConceptRelationModel).where(
                or_(
                    AestheticConceptRelationModel.from_concept_id.in_(concept_ids),
                    AestheticConceptRelationModel.to_concept_id.in_(concept_ids),
                )
            )
        ).all()

        edges: list[ConceptRelation] = []
        related_ids = set(concept_ids)
        for row in rows:
            relation = _relation_from_model(row)
            if relation is None:
                continue
            edges.append(relation)
            related_ids.add(row.from_concept_id)
            related_ids.add(row.to_concept_id)

        concept_rows = self.session.scalars(
            select(AestheticConceptModel).where(AestheticConceptModel.id.in_(related_ids))
        ).all()
        concepts = [_concept_from_model(row) for row in concept_rows]
        return concepts, edges

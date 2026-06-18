from app.ai.knowledge.aesthetic_knowledge_base import AESTHETIC_KNOWLEDGE_CHUNKS
from app.schemas.knowledge_graph import AestheticConcept, ConceptRelation, KnowledgeChunkSummary, SourceEvidence

KNOWLEDGE_GRAPH_DISCLAIMER = (
    "审美概念图谱仅用于解释风格概念之间的关系，不代表用户偏好证据。"
)

CONCEPTS: tuple[AestheticConcept, ...] = (
    AestheticConcept(
        id="concept_low_saturation",
        slug="low-saturation",
        label="低饱和结构",
        description="以低饱和色块和弱对比为主的视觉结构气质。",
        featureTags=["saturation=low", "density=low"],
        sourceRefs=["kb_low_saturation_space"],
    ),
    AestheticConcept(
        id="concept_medium_low_saturation",
        slug="medium-low-saturation",
        label="中低饱和过渡",
        description="中低饱和常用于描述柔和过渡与弱对比场景。",
        featureTags=["saturation=medium-low"],
        sourceRefs=["kb_medium_low_saturation"],
    ),
    AestheticConcept(
        id="concept_person_absent",
        slug="person-absent-composition",
        label="非人物中心构图",
        description="更偏空间、物体或片段意象而非明确人物行动。",
        featureTags=["presence=person_absent"],
        sourceRefs=["kb_person_absent_composition"],
    ),
    AestheticConcept(
        id="concept_low_density",
        slug="low-density-fragment",
        label="低密度片段观察",
        description="元素较少、留白明显的片段式观察结构。",
        featureTags=["density=low", "presence=person_absent"],
        sourceRefs=["kb_low_density_fragment"],
    ),
)

RELATIONS: tuple[ConceptRelation, ...] = (
    ConceptRelation(
        id="rel_low_saturation_low_density",
        fromConceptId="concept_low_saturation",
        toConceptId="concept_low_density",
        predicate="related_to",
        sourceEvidence=SourceEvidence(
            docIds=["kb_low_saturation_space", "kb_low_density_fragment"],
            note="curated from project knowledge v1",
        ),
    ),
    ConceptRelation(
        id="rel_low_saturation_medium_low",
        fromConceptId="concept_low_saturation",
        toConceptId="concept_medium_low_saturation",
        predicate="contrasts_with",
        sourceEvidence=SourceEvidence(
            docIds=["kb_low_saturation_space", "kb_medium_low_saturation"],
            note="curated contrast pair from project knowledge v1",
        ),
    ),
    ConceptRelation(
        id="rel_person_absent_low_density",
        fromConceptId="concept_person_absent",
        toConceptId="concept_low_density",
        predicate="example_of",
        sourceEvidence=SourceEvidence(
            docIds=["kb_person_absent_composition", "kb_low_density_fragment"],
            note="curated example relation from project knowledge v1",
        ),
    ),
)


def knowledge_chunk_summaries() -> list[KnowledgeChunkSummary]:
    return [
        KnowledgeChunkSummary(
            docId=chunk.doc_id,
            title=chunk.title,
            snippet=chunk.snippet,
            featureTags=sorted(chunk.feature_tags),
            source=chunk.source,
        )
        for chunk in AESTHETIC_KNOWLEDGE_CHUNKS
    ]

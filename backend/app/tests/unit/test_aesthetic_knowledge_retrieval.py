from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.schemas.feature import InputFeature
from app.services.aesthetic_knowledge_retrieval import build_aesthetic_knowledge_context
from app.services.knowledge_graph_query import KnowledgeGraphQueryService


def test_aesthetic_knowledge_context_returns_empty_state_without_features() -> None:
    context = build_aesthetic_knowledge_context([])

    assert context.items == []
    assert context.message == "当前输入特征不足，暂时无法匹配审美知识参考。"
    assert context.retrieval_meta is not None
    assert context.retrieval_meta.abstention_reason == "insufficient_features"


def test_aesthetic_knowledge_context_matches_low_saturation_and_density() -> None:
    context = build_aesthetic_knowledge_context(_features(), graph_repository=KnowledgeGraphRepository())

    assert context.items
    assert any(item.doc_id == "kb_low_saturation_space" for item in context.items)
    assert all(item.source_refs for item in context.items)
    assert context.summary is not None
    assert "人格" not in (context.summary or "")


def test_aesthetic_knowledge_context_prefers_relevant_chunks() -> None:
    context = build_aesthetic_knowledge_context(
        _features(presence="person_absent"),
        graph_repository=KnowledgeGraphRepository(),
    )

    doc_ids = {item.doc_id for item in context.items}
    assert "kb_person_absent_composition" in doc_ids


def test_aesthetic_knowledge_context_prefers_higher_feature_overlap() -> None:
    context = build_aesthetic_knowledge_context(_features(), graph_repository=KnowledgeGraphRepository())

    assert context.items
    assert context.items[0].doc_id in {"kb_low_saturation_space", "kb_low_density_fragment"}
    assert len(context.items[0].matched_features) >= 2


def test_aesthetic_knowledge_context_abstains_for_out_of_scope_features() -> None:
    context = build_aesthetic_knowledge_context(
        [
            InputFeature(
                inputId="input_1",
                featureType="text",
                lowLevelFeatures={
                    "color_mood": {
                        "value": "warm",
                        "confidence": 0.8,
                        "evidence": ["evidence_1"],
                    }
                },
                sampleEvidence=["sample evidence"],
                promptVersion="test",
                modelName="mock",
            )
        ],
        graph_repository=KnowledgeGraphRepository(),
    )

    assert context.items == []
    assert context.message == "暂未找到与当前输入足够相关的审美知识参考。"
    assert context.retrieval_meta is not None
    assert context.retrieval_meta.abstention_reason == "no_tag_overlap"


def test_aesthetic_knowledge_context_enriches_with_graph_relations() -> None:
    context = build_aesthetic_knowledge_context(_features(), graph_repository=KnowledgeGraphRepository())

    assert context.items
    assert any(item.related_concept_ids for item in context.items)
    assert any(item.relation_notes for item in context.items)
    assert context.retrieval_meta is not None
    assert context.retrieval_meta.graph_hit_count > 0
    assert context.retrieval_meta.tag_match_count > 0


def test_knowledge_graph_query_lists_seed_concepts() -> None:
    service = KnowledgeGraphQueryService(KnowledgeGraphRepository())
    response = service.list_concepts()

    assert response.total == 4
    assert {concept.id for concept in response.concepts} == {
        "concept_low_saturation",
        "concept_medium_low_saturation",
        "concept_person_absent",
        "concept_low_density",
    }


def test_knowledge_graph_query_expands_one_hop() -> None:
    service = KnowledgeGraphQueryService(KnowledgeGraphRepository())
    graph = service.get_one_hop_graph("concept_low_saturation")

    assert graph is not None
    assert len(graph.edges) >= 2
    assert graph.disclaimer
    assert all(edge.relation.source_evidence.doc_ids for edge in graph.edges)


def test_knowledge_graph_query_filters_by_feature_tag() -> None:
    service = KnowledgeGraphQueryService(KnowledgeGraphRepository())
    response = service.list_concepts(feature_tag="saturation=low")

    assert response.total == 1
    assert response.concepts[0].id == "concept_low_saturation"


def _features(presence: str = "person_absent") -> list[InputFeature]:
    return [
        InputFeature(
            inputId="input_1",
            featureType="text",
            lowLevelFeatures={
                "saturation": {
                    "value": "low",
                    "confidence": 0.8,
                    "evidence": ["evidence_1"],
                },
                "density": {
                    "value": "low",
                    "confidence": 0.7,
                    "evidence": ["evidence_2"],
                },
                "presence": {
                    "value": presence,
                    "confidence": 0.7,
                    "evidence": ["evidence_3"],
                },
            },
            sampleEvidence=["sample evidence"],
            promptVersion="test",
            modelName="mock",
        )
    ]

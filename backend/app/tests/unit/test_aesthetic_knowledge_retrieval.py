from app.schemas.feature import InputFeature
from app.services.aesthetic_knowledge_retrieval import build_aesthetic_knowledge_context


def test_aesthetic_knowledge_context_returns_empty_state_without_features() -> None:
    context = build_aesthetic_knowledge_context([])

    assert context.items == []
    assert context.message == "当前输入特征不足，暂时无法匹配审美知识参考。"


def test_aesthetic_knowledge_context_matches_low_saturation_and_density() -> None:
    context = build_aesthetic_knowledge_context(_features())

    assert context.items
    assert any(item.doc_id == "kb_low_saturation_space" for item in context.items)
    assert all(item.source_refs for item in context.items)
    assert context.summary is not None
    assert "人格" not in (context.summary or "")


def test_aesthetic_knowledge_context_prefers_relevant_chunks() -> None:
    context = build_aesthetic_knowledge_context(_features(presence="person_absent"))

    doc_ids = {item.doc_id for item in context.items}
    assert "kb_person_absent_composition" in doc_ids


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

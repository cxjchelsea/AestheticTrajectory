from app.ai.ollama.ollama_interpretation_generator import OllamaInterpretationGenerator
from app.schemas.feature import FeatureSignal, InputFeature


def test_ollama_generator_builds_payload_from_input_feature_schema(monkeypatch) -> None:
    generator = OllamaInterpretationGenerator("http://127.0.0.1:11434", "test-model", timeout_seconds=5)
    captured: dict[str, str] = {}

    def fake_chat_json(user_message: str) -> dict[str, object]:
        captured["user_message"] = user_message
        return {
            "promptVersion": "interpretations.generate.v1",
            "modelName": "test-model",
            "interpretations": [
                {
                    "id": "interpretation_001",
                    "name": "低密度倾向",
                    "confidence": 0.7,
                    "evidenceRefs": ["input_a"],
                    "uncertainty": "样本较少。",
                }
            ],
            "insights": [
                {
                    "insightId": "insight_001",
                    "title": "观察到低密度结构",
                    "observation": "输入中重复出现低密度特征。",
                    "interpretation": "这可能表示当前样本偏向留白构图。",
                    "evidenceRefs": ["input_a"],
                    "uncertainty": "不是人格诊断。",
                    "confidence": 0.65,
                }
            ],
        }

    monkeypatch.setattr(generator, "_chat_json", fake_chat_json)

    feature = InputFeature(
        inputId="input_a",
        featureType="text",
        lowLevelFeatures={
            "density": FeatureSignal(value="low", confidence=0.8, evidence=["low density"]),
        },
        sampleEvidence=["quiet evidence"],
        promptVersion="text_features.extract.v1",
        modelName="test-feature-extractor",
    )

    interpretations, insights = generator.generate([], [feature], ["input_a"])

    assert interpretations[0].name == "低密度倾向"
    assert insights[0].title == "观察到低密度结构"
    assert '"inputId": "input_a"' in captured["user_message"]
    assert '"featureType": "text"' in captured["user_message"]

from app.ai.mock.mock_interpretation_generator import MockInterpretationGenerator
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.interpretation import SimilarityGroup
from app.workflows.steps.generate_report import generate_report


def test_interpretation_and_insight_use_group_evidence_and_uncertainty() -> None:
    features = [_feature("input_001"), _feature("input_002"), _feature("input_003")]
    groups = [
        SimilarityGroup(
            groupId="group_similarity_001",
            name="低密度相似组",
            inputIds=["input_001", "input_002"],
            commonFeatures=["density:low", "saturation:low"],
            uncertainty="样本数量较少。",
        )
    ]
    generator = MockInterpretationGenerator()

    interpretations = generator.interpret(groups, features, ["input_001", "input_002", "input_003"])
    insights = generator.insights(groups, features, ["input_001", "input_002", "input_003"])

    assert interpretations[0].evidence_refs == ["input_001", "input_002"]
    assert "候选" not in interpretations[0].name
    assert "可能观察" in interpretations[0].uncertainty
    assert insights[0].evidence_refs == ["input_001", "input_002"]
    assert "可能" in insights[0].title
    assert "人格诊断" in insights[0].uncertainty
    assert insights[0].confidence <= 0.72


def test_confidence_is_lowered_when_evidence_is_weak() -> None:
    features = [_feature("input_001")]
    generator = MockInterpretationGenerator()

    interpretations = generator.interpret([], features, ["input_001"])
    insights = generator.insights([], features, ["input_001"])

    assert interpretations[0].confidence <= 0.55
    assert insights[0].confidence <= 0.55


def test_generate_report_summary_uses_observable_features_without_diagnostic_language() -> None:
    features = [_feature("input_001"), _feature("input_002"), _feature("input_003")]
    groups = [
        SimilarityGroup(
            groupId="group_similarity_001",
            name="低密度相似组",
            inputIds=["input_001", "input_002"],
            commonFeatures=["density:low", "saturation:low"],
            uncertainty="样本数量较少。",
        )
    ]
    generator = MockInterpretationGenerator()
    interpretations = generator.interpret(groups, features, ["input_001", "input_002", "input_003"])
    insights = generator.insights(groups, features, ["input_001", "input_002", "input_003"])

    report = generate_report("report_001", features, groups, interpretations, insights)

    assert "density=low" in report.summary
    assert "saturation=low" in report.summary
    assert "倾向" in report.summary
    assert "不是人格诊断" in report.summary
    assert "你一定" not in report.summary
    assert "灵魂" not in report.summary


def test_generate_report_scopes_mock_interpretation_and_insight_ids_by_report() -> None:
    features = [_feature("input_001"), _feature("input_002"), _feature("input_003")]
    groups = [
        SimilarityGroup(
            groupId="group_similarity_001",
            name="低密度相似组",
            inputIds=["input_001", "input_002"],
            commonFeatures=["density:low", "saturation:low"],
            uncertainty="样本数量较少。",
        )
    ]
    generator = MockInterpretationGenerator()
    interpretations = generator.interpret(groups, features, ["input_001", "input_002", "input_003"])
    insights = generator.insights(groups, features, ["input_001", "input_002", "input_003"])

    report = generate_report("report_001", features, groups, interpretations, insights)

    assert report.possible_interpretations[0].id == "report_001_interpretation_mock_001"
    assert report.insights[0].insight_id == "report_001_insight_mock_001"


def _feature(input_id: str) -> InputFeature:
    return InputFeature(
        inputId=input_id,
        featureType="text",
        lowLevelFeatures={
            "density": FeatureSignal(value="low", confidence=0.8, evidence=["low density"]),
            "saturation": FeatureSignal(value="low", confidence=0.7, evidence=["low saturation"]),
        },
        sampleEvidence=["quiet evidence"],
        promptVersion="text_features.extract.v1",
        modelName="test-feature-extractor",
    )

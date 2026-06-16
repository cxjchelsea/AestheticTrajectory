import pytest

from app.ai.heuristic_feature_extractor import HeuristicFeatureExtractor
from app.ai.validators.prompt_output_validator import validate_input_feature
from app.schemas.common import utc_now
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse
from app.workflows.steps.extract_features import extract_features


def test_feature_schema_accepts_v1_mock_shape() -> None:
    feature = InputFeature(
        inputId="input_001",
        featureType="image",
        lowLevelFeatures={
            "saturation": FeatureSignal(
                value="low",
                confidence=0.82,
                evidence=["画面整体以低饱和灰蓝色为主"],
            )
        },
        sampleEvidence=["大面积灰色墙面"],
        promptVersion="image_features.extract.v1",
        modelName="mock-feature-extractor-v1",
    )

    assert feature.input_id == "input_001"
    assert feature.low_level_features["saturation"].confidence == 0.82


def test_input_feature_validator_rejects_empty_signal_evidence() -> None:
    feature = InputFeature(
        inputId="input_001",
        featureType="text",
        lowLevelFeatures={
            "narrativeDensity": FeatureSignal(
                value="low",
                confidence=0.72,
                evidence=["initial evidence"],
            )
        },
        sampleEvidence=["房间里只剩下下午的光"],
        promptVersion="text_features.extract.v1",
        modelName="mock-feature-extractor-v1",
    )
    feature.low_level_features["narrativeDensity"].evidence = []

    with pytest.raises(ValueError, match="must include evidence"):
        validate_input_feature(feature)


def test_extract_features_accepts_injected_heuristic_extractor() -> None:
    input_record = AestheticInputResponse(
        id="input_text_001",
        userId="user_anonymous",
        type="text",
        contentText="房间里只剩下下午的光，回声很轻，像某种被放慢的秩序。",
        fileUrl=None,
        source="test",
        title="空房间片段",
        description=None,
        createdAt=utc_now(),
    )

    features = extract_features([input_record], extractor=HeuristicFeatureExtractor())

    assert features[0].feature_type == "text"
    assert features[0].model_name == "local-heuristic-feature-extractor-v1"
    assert "narrativeDensity" in features[0].low_level_features
    assert features[0].low_level_features["narrativeDensity"].evidence

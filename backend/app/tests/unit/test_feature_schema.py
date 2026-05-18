from app.schemas.feature import FeatureSignal, InputFeature


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
    )

    assert feature.input_id == "input_001"
    assert feature.low_level_features["saturation"].confidence == 0.82

import importlib

import pytest

from app.schemas.common import utc_now
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


def _image_input() -> AestheticInputResponse:
    return AestheticInputResponse(
        id="input_image_001",
        userId="user_anonymous",
        type="image",
        contentText=None,
        fileUrl="/api/files/file_image_001",
        source="test",
        title="test image",
        description="uploaded image",
        createdAt=utc_now(),
    )


def test_v6a_default_mock_image_feature_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_FEATURE_RUNTIME", "mock")
    from app.workflows.steps.extract_features import extract_features

    features = extract_features([_image_input()])

    assert len(features) == 1
    feature = features[0]
    assert feature.feature_type == "image"
    assert feature.model_name == "mock-image-feature-extractor-v6a"
    assert feature.low_level_features["imageParsingStatus"].value == "placeholder"
    assert "dev-only" in feature.low_level_features["imageParsingStatus"].evidence[0]


def test_v6a_disabled_image_feature_runtime_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_FEATURE_RUNTIME", "disabled")
    from app.workflows.steps.extract_features import extract_features

    with pytest.raises(ValueError, match="IMAGE_FEATURE_RUNTIME=disabled"):
        extract_features([_image_input()])


def test_v6a_ollama_vision_invalid_json_fails_fast(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    import app.ai.image_feature_extractor as image_module

    image_path = tmp_path / "image.png"
    image_path.write_bytes(b"fake image bytes")

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"response": "not-json"}

    monkeypatch.setattr(image_module, "_resolve_local_image", lambda input_record: image_path)
    monkeypatch.setattr(image_module.httpx, "post", lambda *args, **kwargs: FakeResponse())

    extractor = image_module.OllamaVisionImageFeatureExtractor(
        base_url="http://127.0.0.1:11434",
        model_name="vision-test",
        timeout_seconds=1,
    )

    with pytest.raises(ValueError, match="not valid JSON"):
        extractor.extract(_image_input(), 0)


def test_v6a_image_feature_governance_rejects_diagnostic_claim() -> None:
    from app.ai.image_feature_extractor import validate_image_feature

    feature = InputFeature(
        inputId="input_image_001",
        featureType="image",
        lowLevelFeatures={
            "composition": FeatureSignal(
                value="说明你是孤僻的人",
                confidence=0.7,
                evidence=["画面中有一个人物，所以进行人格诊断。"],
            )
        },
        sampleEvidence=["test"],
        promptVersion="image_features.extract.v6a",
        modelName="vision-test",
    )

    with pytest.raises(ValueError, match="governance boundary"):
        validate_image_feature(feature)


def test_v6a_debug_mock_usage_marks_image_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_FEATURE_RUNTIME", "mock")
    import app.services.analysis_job_service as service_module

    importlib.reload(service_module)
    components = {item.component: item for item in service_module._mock_usage()}

    assert components["MockImageFeatureExtractor"].status == "enabled"
    assert components["MockImageFeatureExtractor"].dev_only is True


def test_v6a_debug_mock_usage_marks_ollama_vision_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IMAGE_FEATURE_RUNTIME", "ollama_vision")
    monkeypatch.setenv("IMAGE_FEATURE_MODEL", "vision-test")
    import app.services.analysis_job_service as service_module

    importlib.reload(service_module)
    components = {item.component: item for item in service_module._mock_usage()}

    assert components["OllamaVisionImageFeatureExtractor"].status == "disabled"
    assert components["MockImageFeatureExtractor"].status == "disabled"

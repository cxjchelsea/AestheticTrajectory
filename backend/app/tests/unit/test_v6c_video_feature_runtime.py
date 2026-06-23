import importlib

import pytest

from app.schemas.common import utc_now
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


def _video_input(
    *,
    content_text: str | None = None,
    description: str | None = None,
) -> AestheticInputResponse:
    return AestheticInputResponse(
        id="input_video_001",
        userId="user_anonymous",
        type="video",
        contentText=content_text,
        fileUrl="https://example.com/video",
        source="test",
        title="test video",
        description=description,
        createdAt=utc_now(),
    )


def test_v6c_default_metadata_only_video_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "metadata_only")
    from app.workflows.steps.extract_features import extract_features

    features = extract_features([_video_input()])

    assert len(features) == 1
    feature = features[0]
    assert feature.feature_type == "video"
    assert feature.model_name == "metadata-video-feature-extractor-v6c"
    assert feature.low_level_features["videoParsingStatus"].value == "metadata_only"
    assert "no frames or subtitles were parsed" in feature.low_level_features["videoParsingStatus"].evidence[0]


def test_v6c_text_notes_video_runtime_uses_user_provided_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "text_notes")
    from app.workflows.steps.extract_features import extract_features

    features = extract_features(
        [
            _video_input(
                content_text="字幕：夜里的街道很安静。分镜说明：缓慢停顿后切到室内独白。",
                description=None,
            )
        ]
    )

    feature = features[0]
    assert feature.model_name == "text-notes-video-feature-extractor-v6c"
    assert feature.low_level_features["videoParsingStatus"].value == "subtitle_or_description_parsed"
    assert feature.low_level_features["sourceTextType"].value == "subtitle"
    assert feature.low_level_features["sceneImagery"].value == "spatial_or_scene"
    assert feature.low_level_features["pacingImpression"].value == "slow"
    assert "夜里的街道" in feature.sample_evidence[0]


def test_v6c_text_notes_runtime_falls_back_to_metadata_without_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "text_notes")
    from app.workflows.steps.extract_features import extract_features

    feature = extract_features([_video_input()])[0]

    assert feature.low_level_features["videoParsingStatus"].value == "metadata_only"


def test_v6c_disabled_video_runtime_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "disabled")
    from app.workflows.steps.extract_features import extract_features

    with pytest.raises(ValueError, match="VIDEO_FEATURE_RUNTIME=disabled"):
        extract_features([_video_input()])


def test_v6c_metadata_only_validator_rejects_visual_content_claim() -> None:
    from app.ai.video_feature_extractor import validate_video_feature

    feature = InputFeature(
        inputId="input_video_001",
        featureType="video",
        lowLevelFeatures={
            "videoParsingStatus": FeatureSignal(
                value="metadata_only",
                confidence=1.0,
                evidence=["只看标题，但这里声称看到画面和镜头运动。"],
            ),
            "visualNarrative": FeatureSignal(
                value="shot_notes",
                confidence=0.7,
                evidence=["看见快速剪辑和光线变化。"],
            ),
        },
        sampleEvidence=["test"],
        promptVersion="video_features.extract.v6c",
        modelName="metadata-test",
    )

    with pytest.raises(ValueError, match="cannot claim parsed video content"):
        validate_video_feature(feature)


def test_v6c_video_feature_governance_rejects_identity_or_diagnostic_claim() -> None:
    from app.ai.video_feature_extractor import validate_video_feature

    feature = InputFeature(
        inputId="input_video_001",
        featureType="video",
        lowLevelFeatures={
            "videoParsingStatus": FeatureSignal(
                value="subtitle_or_description_parsed",
                confidence=1.0,
                evidence=["用户提供字幕。"],
            ),
            "visualNarrative": FeatureSignal(
                value="说明你是命运感很强的人",
                confidence=0.7,
                evidence=["把字幕解读成人格诊断。"],
            ),
        },
        sampleEvidence=["test"],
        promptVersion="video_features.extract.v6c",
        modelName="video-test",
    )

    with pytest.raises(ValueError, match="governance boundary"):
        validate_video_feature(feature)


def test_v6c_debug_mock_usage_marks_video_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "metadata_only")
    import app.services.analysis_job_service as service_module

    importlib.reload(service_module)
    components = {item.component: item for item in service_module._mock_usage()}

    assert components["MetadataOnlyVideoFeatureExtractor"].status == "disabled"
    assert components["MockVideoFeatureExtractor"].status == "disabled"


def test_v6c_debug_mock_usage_marks_mock_video_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FEATURE_RUNTIME", "mock")
    import app.services.analysis_job_service as service_module

    importlib.reload(service_module)
    components = {item.component: item for item in service_module._mock_usage()}

    assert components["MockVideoFeatureExtractor"].status == "enabled"
    assert components["MockVideoFeatureExtractor"].dev_only is True

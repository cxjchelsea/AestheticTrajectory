import importlib

import pytest

from app.schemas.common import utc_now
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


def _music_input(
    *,
    content_text: str | None = None,
    description: str | None = None,
) -> AestheticInputResponse:
    return AestheticInputResponse(
        id="input_music_001",
        userId="user_anonymous",
        type="music",
        contentText=content_text,
        fileUrl="https://example.com/track",
        source="test",
        title="test track",
        description=description,
        createdAt=utc_now(),
    )


def test_v6b_default_metadata_only_music_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "metadata_only")
    from app.workflows.steps.extract_features import extract_features

    features = extract_features([_music_input()])

    assert len(features) == 1
    feature = features[0]
    assert feature.feature_type == "music"
    assert feature.model_name == "metadata-music-feature-extractor-v6b"
    assert feature.low_level_features["musicParsingStatus"].value == "metadata_only"
    assert "no audio content was parsed" in feature.low_level_features["musicParsingStatus"].evidence[0]


def test_v6b_text_notes_music_runtime_uses_user_provided_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "text_notes")
    from app.workflows.steps.extract_features import extract_features

    features = extract_features(
        [
            _music_input(
                content_text="歌词：夜色和雨反复出现，整体听感安静、缓慢。",
                description=None,
            )
        ]
    )

    feature = features[0]
    assert feature.model_name == "text-notes-music-feature-extractor-v6b"
    assert feature.low_level_features["musicParsingStatus"].value == "lyrics_or_transcript_parsed"
    assert feature.low_level_features["sourceTextType"].value == "lyrics"
    assert feature.low_level_features["lyricalImagery"].value == "spatial_or_scene"
    assert "夜色和雨" in feature.sample_evidence[0]


def test_v6b_text_notes_runtime_falls_back_to_metadata_without_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "text_notes")
    from app.workflows.steps.extract_features import extract_features

    feature = extract_features([_music_input()])[0]

    assert feature.low_level_features["musicParsingStatus"].value == "metadata_only"


def test_v6b_disabled_music_runtime_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "disabled")
    from app.workflows.steps.extract_features import extract_features

    with pytest.raises(ValueError, match="MUSIC_FEATURE_RUNTIME=disabled"):
        extract_features([_music_input()])


def test_v6b_metadata_only_validator_rejects_audio_content_claim() -> None:
    from app.ai.audio_music_feature_extractor import validate_audio_music_feature

    feature = InputFeature(
        inputId="input_music_001",
        featureType="music",
        lowLevelFeatures={
            "musicParsingStatus": FeatureSignal(
                value="metadata_only",
                confidence=1.0,
                evidence=["只看标题，但这里声称听见鼓点。"],
            ),
            "moodTone": FeatureSignal(
                value="bright",
                confidence=0.7,
                evidence=["听到明亮旋律。"],
            ),
        },
        sampleEvidence=["test"],
        promptVersion="music_features.extract.v6b",
        modelName="metadata-test",
    )

    with pytest.raises(ValueError, match="cannot claim parsed audio content"):
        validate_audio_music_feature(feature)


def test_v6b_music_feature_governance_rejects_diagnostic_claim() -> None:
    from app.ai.audio_music_feature_extractor import validate_audio_music_feature

    feature = InputFeature(
        inputId="input_music_001",
        featureType="music",
        lowLevelFeatures={
            "musicParsingStatus": FeatureSignal(
                value="lyrics_or_transcript_parsed",
                confidence=1.0,
                evidence=["用户提供歌词。"],
            ),
            "moodTone": FeatureSignal(
                value="说明你是命运感很强的人",
                confidence=0.7,
                evidence=["把歌词解读成人格诊断。"],
            ),
        },
        sampleEvidence=["test"],
        promptVersion="music_features.extract.v6b",
        modelName="music-test",
    )

    with pytest.raises(ValueError, match="governance boundary"):
        validate_audio_music_feature(feature)


def test_v6b_debug_mock_usage_marks_music_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "metadata_only")
    import app.services.analysis_job_service as service_module

    importlib.reload(service_module)
    components = {item.component: item for item in service_module._mock_usage()}

    assert components["MetadataOnlyAudioMusicFeatureExtractor"].status == "disabled"
    assert components["MockAudioMusicFeatureExtractor"].status == "disabled"


def test_v6b_debug_mock_usage_marks_mock_music_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MUSIC_FEATURE_RUNTIME", "mock")
    import app.services.analysis_job_service as service_module

    importlib.reload(service_module)
    components = {item.component: item for item in service_module._mock_usage()}

    assert components["MockAudioMusicFeatureExtractor"].status == "enabled"
    assert components["MockAudioMusicFeatureExtractor"].dev_only is True

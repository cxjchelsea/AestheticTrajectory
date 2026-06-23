from app.ai.validators.prompt_output_validator import validate_input_feature
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


MUSIC_FEATURE_PROMPT_VERSION = "music_features.extract.v6b"
MOCK_MUSIC_MODEL_NAME = "mock-music-feature-extractor-v6b"
METADATA_MUSIC_MODEL_NAME = "metadata-music-feature-extractor-v6b"
TEXT_NOTES_MUSIC_MODEL_NAME = "text-notes-music-feature-extractor-v6b"
BANNED_MUSIC_GOVERNANCE_PHRASES = (
    "人格诊断",
    "心理疾病",
    "心理问题",
    "能力强",
    "能力弱",
    "命运",
    "说明你是",
)
UNSUPPORTED_METADATA_AUDIO_CLAIMS = (
    "听见",
    "听到",
    "鼓点",
    "旋律",
    "音色",
    "节拍",
    "和声",
    "人声",
    "贝斯",
    "吉他",
)


class DisabledAudioMusicFeatureExtractor:
    model_name = "disabled-music-feature-runtime"

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        raise ValueError(
            "MUSIC_FEATURE_RUNTIME=disabled cannot extract music content; "
            "use metadata_only for truthful metadata handling or text_notes for user-provided notes."
        )


class MockAudioMusicFeatureExtractor:
    model_name = MOCK_MUSIC_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        feature = InputFeature(
            inputId=input_record.id,
            featureType="music",
            lowLevelFeatures={
                "musicParsingStatus": FeatureSignal(
                    value="placeholder",
                    confidence=1.0,
                    evidence=["V6-B mock music path: this is a dev-only placeholder, not real audio understanding."],
                ),
                "moodTone": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["Mock path did not read audio or user-provided notes."],
                ),
            },
            sampleEvidence=[
                input_record.title or input_record.id,
                input_record.description or input_record.file_url or "mock music feature placeholder",
            ],
            promptVersion="music_features.mock.v6b",
            modelName=self.model_name,
        )
        return validate_audio_music_feature(feature)


class MetadataOnlyAudioMusicFeatureExtractor:
    model_name = METADATA_MUSIC_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        metadata = _metadata_evidence(input_record)
        feature = InputFeature(
            inputId=input_record.id,
            featureType="music",
            lowLevelFeatures={
                "musicParsingStatus": FeatureSignal(
                    value="metadata_only",
                    confidence=1.0,
                    evidence=["Only user-provided music metadata was used; no audio content was parsed."],
                ),
                "sourceTextType": FeatureSignal(
                    value=_metadata_source_type(input_record),
                    confidence=1.0,
                    evidence=[metadata],
                ),
                "moodTone": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["Metadata-only path cannot infer mood, rhythm, timbre, or listening experience."],
                ),
            },
            sampleEvidence=[metadata],
            promptVersion=MUSIC_FEATURE_PROMPT_VERSION,
            modelName=self.model_name,
        )
        return validate_audio_music_feature(feature)


class TextNotesAudioMusicFeatureExtractor:
    model_name = TEXT_NOTES_MUSIC_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        note_text = _user_music_text(input_record)
        if not note_text:
            return MetadataOnlyAudioMusicFeatureExtractor().extract(input_record, index)

        compact = _compact(note_text)
        feature = InputFeature(
            inputId=input_record.id,
            featureType="music",
            lowLevelFeatures={
                "musicParsingStatus": FeatureSignal(
                    value="lyrics_or_transcript_parsed",
                    confidence=1.0,
                    evidence=["User-provided lyrics, transcript, or listening notes were parsed as text evidence."],
                ),
                "sourceTextType": FeatureSignal(
                    value=_text_source_type(input_record),
                    confidence=1.0,
                    evidence=[compact],
                ),
                "lyricalImagery": FeatureSignal(
                    value=_imagery_value(note_text),
                    confidence=0.68,
                    evidence=[compact],
                ),
                "moodTone": FeatureSignal(
                    value=_mood_value(note_text),
                    confidence=0.66,
                    evidence=[compact],
                ),
            },
            sampleEvidence=[compact],
            promptVersion=MUSIC_FEATURE_PROMPT_VERSION,
            modelName=self.model_name,
        )
        return validate_audio_music_feature(feature)


def validate_audio_music_feature(feature: InputFeature) -> InputFeature:
    validated = validate_input_feature(feature)
    if validated.feature_type != "music":
        raise ValueError("Audio/music feature extractor must return featureType=music")

    status = validated.low_level_features.get("musicParsingStatus")
    if status is None:
        raise ValueError("Music feature output must include musicParsingStatus")
    if status.value not in {"metadata_only", "lyrics_or_transcript_parsed", "placeholder", "failed"}:
        raise ValueError(f"Unsupported musicParsingStatus={status.value}")

    combined = _feature_text(validated)
    for phrase in BANNED_MUSIC_GOVERNANCE_PHRASES:
        if phrase in combined:
            raise ValueError(f"Music feature output violates governance boundary: {phrase}")

    if status.value == "metadata_only":
        for claim in UNSUPPORTED_METADATA_AUDIO_CLAIMS:
            if claim in combined:
                raise ValueError(f"Metadata-only music feature cannot claim parsed audio content: {claim}")
    return validated


def _feature_text(feature: InputFeature) -> str:
    text_parts: list[str] = [feature.prompt_version, feature.model_name, *feature.sample_evidence]
    for name, signal in feature.low_level_features.items():
        text_parts.append(name)
        text_parts.append(signal.value)
        text_parts.extend(signal.evidence)
    return "\n".join(text_parts)


def _user_music_text(input_record: AestheticInputResponse) -> str:
    return input_record.content_text or input_record.description or ""


def _metadata_evidence(input_record: AestheticInputResponse) -> str:
    parts = [input_record.title or "", input_record.file_url or "", input_record.description or ""]
    return _compact(" / ".join(part for part in parts if part)) or input_record.id


def _metadata_source_type(input_record: AestheticInputResponse) -> str:
    if input_record.title:
        return "title"
    if input_record.description:
        return "description"
    if input_record.file_url:
        return "url"
    return "metadata"


def _text_source_type(input_record: AestheticInputResponse) -> str:
    text = _user_music_text(input_record).lower()
    if any(marker in text for marker in ("歌词", "lyrics", "verse", "chorus")):
        return "lyrics"
    if any(marker in text for marker in ("转录", "transcript", "旁白")):
        return "transcript"
    return "notes"


def _imagery_value(text: str) -> str:
    if any(marker in text for marker in ("夜", "海", "雨", "光", "房间", "城市", "天空")):
        return "spatial_or_scene"
    if any(marker in text for marker in ("记忆", "梦", "孤独", "告别", "时间")):
        return "emotional_memory"
    return "not_enough_textual_evidence"


def _mood_value(text: str) -> str:
    if any(marker in text for marker in ("安静", "低沉", "缓慢", "冷", "柔和")):
        return "quiet"
    if any(marker in text for marker in ("明亮", "热烈", "快速", "兴奋")):
        return "bright"
    return "neutral"


def _compact(text: str) -> str:
    return " ".join(text.split())[:120]

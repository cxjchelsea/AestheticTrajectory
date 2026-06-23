from app.ai.validators.prompt_output_validator import validate_input_feature
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


VIDEO_FEATURE_PROMPT_VERSION = "video_features.extract.v6c"
MOCK_VIDEO_MODEL_NAME = "mock-video-feature-extractor-v6c"
METADATA_VIDEO_MODEL_NAME = "metadata-video-feature-extractor-v6c"
TEXT_NOTES_VIDEO_MODEL_NAME = "text-notes-video-feature-extractor-v6c"
BANNED_VIDEO_GOVERNANCE_PHRASES = (
    "人格诊断",
    "心理疾病",
    "心理问题",
    "能力强",
    "能力弱",
    "命运",
    "说明你是",
    "年龄",
    "性别",
    "身份",
)
UNSUPPORTED_METADATA_VIDEO_CLAIMS = (
    "看见",
    "看到",
    "镜头",
    "画面",
    "剪辑",
    "运动",
    "转场",
    "构图",
    "光线",
    "色彩",
    "人物",
    "字幕显示",
)


class DisabledVideoFeatureExtractor:
    model_name = "disabled-video-feature-runtime"

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        raise ValueError(
            "VIDEO_FEATURE_RUNTIME=disabled cannot extract video content; "
            "use metadata_only for truthful metadata handling or text_notes for user-provided subtitles/notes."
        )


class MockVideoFeatureExtractor:
    model_name = MOCK_VIDEO_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        feature = InputFeature(
            inputId=input_record.id,
            featureType="video",
            lowLevelFeatures={
                "videoParsingStatus": FeatureSignal(
                    value="placeholder",
                    confidence=1.0,
                    evidence=["V6-C mock video path: this is a dev-only placeholder, not real video understanding."],
                ),
                "visualNarrative": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["Mock path did not read frames, subtitles, or user-provided notes."],
                ),
            },
            sampleEvidence=[
                input_record.title or input_record.id,
                input_record.description or input_record.file_url or "mock video feature placeholder",
            ],
            promptVersion="video_features.mock.v6c",
            modelName=self.model_name,
        )
        return validate_video_feature(feature)


class MetadataOnlyVideoFeatureExtractor:
    model_name = METADATA_VIDEO_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        metadata = _metadata_evidence(input_record)
        feature = InputFeature(
            inputId=input_record.id,
            featureType="video",
            lowLevelFeatures={
                "videoParsingStatus": FeatureSignal(
                    value="metadata_only",
                    confidence=1.0,
                    evidence=["Only user-provided video metadata was used; no frames or subtitles were parsed."],
                ),
                "sourceTextType": FeatureSignal(
                    value=_metadata_source_type(input_record),
                    confidence=1.0,
                    evidence=[metadata],
                ),
                "visualNarrative": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["Metadata-only path cannot infer scenes, editing, motion, color, or camera work."],
                ),
            },
            sampleEvidence=[metadata],
            promptVersion=VIDEO_FEATURE_PROMPT_VERSION,
            modelName=self.model_name,
        )
        return validate_video_feature(feature)


class TextNotesVideoFeatureExtractor:
    model_name = TEXT_NOTES_VIDEO_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        note_text = _user_video_text(input_record)
        if not note_text:
            return MetadataOnlyVideoFeatureExtractor().extract(input_record, index)

        compact = _compact(note_text)
        feature = InputFeature(
            inputId=input_record.id,
            featureType="video",
            lowLevelFeatures={
                "videoParsingStatus": FeatureSignal(
                    value="subtitle_or_description_parsed",
                    confidence=1.0,
                    evidence=["User-provided subtitles, description, or shot notes were parsed as text evidence."],
                ),
                "sourceTextType": FeatureSignal(
                    value=_text_source_type(input_record),
                    confidence=1.0,
                    evidence=[compact],
                ),
                "sceneImagery": FeatureSignal(
                    value=_scene_imagery_value(note_text),
                    confidence=0.68,
                    evidence=[compact],
                ),
                "pacingImpression": FeatureSignal(
                    value=_pacing_value(note_text),
                    confidence=0.64,
                    evidence=[compact],
                ),
                "visualNarrative": FeatureSignal(
                    value=_narrative_value(note_text),
                    confidence=0.66,
                    evidence=[compact],
                ),
            },
            sampleEvidence=[compact],
            promptVersion=VIDEO_FEATURE_PROMPT_VERSION,
            modelName=self.model_name,
        )
        return validate_video_feature(feature)


def validate_video_feature(feature: InputFeature) -> InputFeature:
    validated = validate_input_feature(feature)
    if validated.feature_type != "video":
        raise ValueError("Video feature extractor must return featureType=video")

    status = validated.low_level_features.get("videoParsingStatus")
    if status is None:
        raise ValueError("Video feature output must include videoParsingStatus")
    if status.value not in {"metadata_only", "subtitle_or_description_parsed", "placeholder", "failed"}:
        raise ValueError(f"Unsupported videoParsingStatus={status.value}")

    combined = _feature_text(validated)
    for phrase in BANNED_VIDEO_GOVERNANCE_PHRASES:
        if phrase in combined:
            raise ValueError(f"Video feature output violates governance boundary: {phrase}")

    if status.value == "metadata_only":
        for claim in UNSUPPORTED_METADATA_VIDEO_CLAIMS:
            if claim in combined:
                raise ValueError(f"Metadata-only video feature cannot claim parsed video content: {claim}")
    return validated


def _feature_text(feature: InputFeature) -> str:
    text_parts: list[str] = [feature.prompt_version, feature.model_name, *feature.sample_evidence]
    for name, signal in feature.low_level_features.items():
        text_parts.append(name)
        text_parts.append(signal.value)
        text_parts.extend(signal.evidence)
    return "\n".join(text_parts)


def _user_video_text(input_record: AestheticInputResponse) -> str:
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
    text = _user_video_text(input_record).lower()
    if any(marker in text for marker in ("字幕", "subtitle", "caption")):
        return "subtitle"
    if any(marker in text for marker in ("分镜", "shot", "镜头说明", "镜头笔记")):
        return "shot_notes"
    if input_record.description:
        return "description"
    return "notes"


def _scene_imagery_value(text: str) -> str:
    if any(marker in text for marker in ("房间", "街道", "城市", "海", "雨", "夜", "天空", "室内")):
        return "spatial_or_scene"
    if any(marker in text for marker in ("回忆", "梦", "告别", "等待", "独白")):
        return "emotional_memory"
    return "not_enough_textual_evidence"


def _pacing_value(text: str) -> str:
    if any(marker in text for marker in ("缓慢", "慢镜头", "停顿", "静止")):
        return "slow"
    if any(marker in text for marker in ("快速", "切换", "追逐", "连续")):
        return "fast"
    return "not_enough_textual_evidence"


def _narrative_value(text: str) -> str:
    if any(marker in text for marker in ("旁白", "字幕", "独白", "对话")):
        return "textual_narrative"
    if any(marker in text for marker in ("分镜", "镜头说明", "shot")):
        return "shot_notes"
    return "descriptive_notes"


def _compact(text: str) -> str:
    return " ".join(text.split())[:120]

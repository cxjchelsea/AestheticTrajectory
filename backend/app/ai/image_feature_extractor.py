import base64
import json
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.ai.validators.prompt_output_validator import validate_input_feature
from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse
from app.storage.file_storage import resolve_uploaded_file


IMAGE_FEATURE_PROMPT_VERSION = "image_features.extract.v6a"
MOCK_IMAGE_MODEL_NAME = "mock-image-feature-extractor-v6a"
BANNED_IMAGE_GOVERNANCE_PHRASES = (
    "人格诊断",
    "心理疾病",
    "心理问题",
    "能力强",
    "能力弱",
    "命运",
    "说明你是",
)


class DisabledImageFeatureExtractor:
    model_name = "disabled-image-feature-runtime"

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        raise ValueError(
            "IMAGE_FEATURE_RUNTIME=disabled cannot extract image content; "
            "use mock for dev-only placeholder behavior or configure ollama_vision."
        )


class MockImageFeatureExtractor:
    model_name = MOCK_IMAGE_MODEL_NAME

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        feature = InputFeature(
            inputId=input_record.id,
            featureType="image",
            lowLevelFeatures={
                "imageParsingStatus": FeatureSignal(
                    value="placeholder",
                    confidence=1.0,
                    evidence=["V6-A mock image path: this is a dev-only placeholder, not real image understanding."],
                ),
                "saturation": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["Mock path did not read image pixels, so saturation is unknown."],
                ),
                "composition": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["Mock path did not inspect composition; configure real vision runtime for analysis."],
                ),
            },
            sampleEvidence=[
                input_record.title or input_record.id,
                input_record.description or input_record.file_url or "mock image feature placeholder",
            ],
            promptVersion="image_features.mock.v6a",
            modelName=self.model_name,
        )
        return validate_image_feature(feature)


class OllamaVisionImageFeatureExtractor:
    def __init__(self, *, base_url: str, model_name: str, timeout_seconds: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        image_path = _resolve_local_image(input_record)
        image_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": _image_prompt(input_record),
                "images": [image_b64],
                "stream": False,
                "format": "json",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        raw_output = payload.get("response")
        if not isinstance(raw_output, str) or not raw_output.strip():
            raise ValueError("Ollama vision response did not include a JSON response string")
        try:
            feature_payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise ValueError("Ollama vision response was not valid JSON") from exc

        feature_payload.setdefault("inputId", input_record.id)
        feature_payload.setdefault("featureType", "image")
        feature_payload.setdefault("promptVersion", IMAGE_FEATURE_PROMPT_VERSION)
        feature_payload.setdefault("modelName", self.model_name)
        return validate_image_feature(InputFeature.model_validate(feature_payload))


def validate_image_feature(feature: InputFeature) -> InputFeature:
    validated = validate_input_feature(feature)
    if validated.feature_type != "image":
        raise ValueError("Image feature extractor must return featureType=image")

    text_parts: list[str] = [validated.prompt_version, validated.model_name, *validated.sample_evidence]
    for name, signal in validated.low_level_features.items():
        text_parts.append(name)
        text_parts.append(signal.value)
        text_parts.extend(signal.evidence)
    combined = "\n".join(text_parts)
    for phrase in BANNED_IMAGE_GOVERNANCE_PHRASES:
        if phrase in combined:
            raise ValueError(f"Image feature output violates governance boundary: {phrase}")
    return validated


def _resolve_local_image(input_record: AestheticInputResponse) -> Path:
    file_url = input_record.file_url or ""
    parsed = urlparse(file_url)
    path = parsed.path or file_url
    marker = "/api/files/"
    if marker not in path:
        raise ValueError("Ollama vision image extraction requires a local uploaded /api/files/{file_id} URL")
    file_id = path.rsplit("/", 1)[-1]
    image_path = resolve_uploaded_file(file_id, user_id=input_record.user_id)
    if image_path is None:
        raise ValueError(f"Uploaded image file not found for {file_id}")
    return image_path


def _image_prompt(input_record: AestheticInputResponse) -> str:
    title = input_record.title or ""
    description = input_record.description or ""
    return f"""You are extracting evidence-bound aesthetic image features.
Return ONLY valid JSON matching this shape:
{{
  "lowLevelFeatures": {{
    "saturation": {{"value": "low|medium-low|medium|high|unknown", "confidence": 0.0, "evidence": ["visible image evidence"]}},
    "density": {{"value": "low|medium|high|unknown", "confidence": 0.0, "evidence": ["visible image evidence"]}},
    "composition": {{"value": "centered|spatial|fragmented|layered|unknown", "confidence": 0.0, "evidence": ["visible image evidence"]}},
    "lighting": {{"value": "soft|harsh|dim|bright|unknown", "confidence": 0.0, "evidence": ["visible image evidence"]}},
    "presence": {{"value": "person_absent|person_present|unclear", "confidence": 0.0, "evidence": ["visible image evidence"]}}
  }},
  "sampleEvidence": ["short visible image evidence"]
}}

Do not infer personality, psychology, ability, fate, identity, or private traits.
User title: {title}
User description: {description}
"""

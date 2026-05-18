from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


class MockFeatureExtractor:
    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        is_text = input_record.type == "text"
        return InputFeature(
            inputId=input_record.id,
            featureType=input_record.type,
            lowLevelFeatures={
                "saturation": FeatureSignal(
                    value="low" if index % 2 == 0 else "medium-low",
                    confidence=0.78,
                    evidence=["文本使用低明度意象"] if is_text else ["画面整体以低饱和色块为主"],
                ),
                "density": FeatureSignal(
                    value="low",
                    confidence=0.72,
                    evidence=["叙事更接近片段观察"] if is_text else ["画面元素数量较少，留白明显"],
                ),
                "presence": FeatureSignal(
                    value="person_absent",
                    confidence=0.69,
                    evidence=["没有明确人物行动"] if is_text else ["主体更偏空间或物体而非人物"],
                ),
            },
            sampleEvidence=[input_record.title or input_record.id, input_record.description or input_record.content_text or ""],
            promptVersion="text_features.extract.v1" if is_text else "image_features.extract.v1",
        )

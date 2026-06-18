from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


class MockFeatureExtractor:
    model_name = "mock-feature-extractor-v1"

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        is_text = input_record.type == "text"
        is_music = input_record.type == "music"
        is_video = input_record.type == "video"
        evidence = (
            ["文本使用低明度意象"]
            if is_text
            else ["元数据提示偏冷静/低饱和审美参考"]
            if is_music or is_video
            else ["画面整体以低饱和色块为主"]
        )
        return InputFeature(
            inputId=input_record.id,
            featureType=input_record.type,
            lowLevelFeatures={
                "saturation": FeatureSignal(
                    value="low" if index % 2 == 0 else "medium-low",
                    confidence=0.78,
                    evidence=evidence,
                ),
                "density": FeatureSignal(
                    value="low",
                    confidence=0.72,
                    evidence=["叙事更接近片段观察"] if is_text else ["元素密度较低，留白明显"],
                ),
                "presence": FeatureSignal(
                    value="person_absent",
                    confidence=0.69,
                    evidence=["没有明确人物行动"] if is_text else ["主体更偏空间或氛围而非人物"],
                ),
            },
            sampleEvidence=[
                input_record.title or input_record.id,
                input_record.description or input_record.content_text or input_record.file_url or "",
            ],
            promptVersion=f"{input_record.type}_features.extract.v1",
            modelName=self.model_name,
        )

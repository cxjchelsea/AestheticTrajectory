from app.schemas.feature import FeatureSignal, InputFeature
from app.schemas.input import AestheticInputResponse


class HeuristicFeatureExtractor:
    """Local extractor boundary used until real LLM / vision clients are wired."""

    model_name = "local-heuristic-feature-extractor-v1"

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        if input_record.type == "text":
            return self._extract_text(input_record)
        return self._extract_image_placeholder(input_record, index)

    def _extract_text(self, input_record: AestheticInputResponse) -> InputFeature:
        text = input_record.content_text or input_record.description or input_record.title or ""
        lowered = text.lower()
        quiet_markers = ["空", "慢", "轻", "安静", "留白", "回声", "秩序", "冷", "灰"]
        dense_markers = ["拥挤", "热闹", "复杂", "强烈", "快速", "明亮"]
        image_markers = ["房间", "光", "空间", "墙", "影", "颜色", "风"]

        quiet_count = sum(marker in lowered for marker in quiet_markers)
        dense_count = sum(marker in lowered for marker in dense_markers)
        image_count = sum(marker in lowered for marker in image_markers)

        density_value = "low" if quiet_count >= dense_count else "medium"
        abstraction_value = "medium" if image_count else "high"
        distance_value = "distant" if any(marker in text for marker in ["房间", "空间", "远", "外"]) else "neutral"

        return InputFeature(
            inputId=input_record.id,
            featureType="text",
            lowLevelFeatures={
                "sentimentTone": FeatureSignal(
                    value="quiet" if quiet_count else "neutral",
                    confidence=0.74 if quiet_count else 0.58,
                    evidence=[self._evidence(text, "文本中出现安静、低刺激或留白相关意象")],
                ),
                "narrativeDensity": FeatureSignal(
                    value=density_value,
                    confidence=0.7,
                    evidence=[self._evidence(text, "文本更偏片段式观察，而不是完整事件叙述")],
                ),
                "imageryType": FeatureSignal(
                    value="spatial" if image_count else "abstract",
                    confidence=0.68,
                    evidence=[self._evidence(text, "文本中出现空间、光线或物象线索")],
                ),
                "subjectDistance": FeatureSignal(
                    value=distance_value,
                    confidence=0.64,
                    evidence=[self._evidence(text, "文本主体更偏观察距离，而非直接行动")],
                ),
            },
            sampleEvidence=[text[:80] or input_record.id],
            promptVersion="text_features.heuristic.v1",
            modelName=self.model_name,
        )

    def _extract_image_placeholder(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        return InputFeature(
            inputId=input_record.id,
            featureType="image",
            lowLevelFeatures={
                "imageStorageStatus": FeatureSignal(
                    value="placeholder_only",
                    confidence=1.0,
                    evidence=["图片真实分析依赖后续文件存储接入；当前只记录占位信息。"],
                ),
                "saturation": FeatureSignal(
                    value="unknown",
                    confidence=0.0,
                    evidence=["当前没有读取图片内容，不能判断真实色彩特征。"],
                ),
            },
            sampleEvidence=[input_record.title or f"image placeholder {index}"],
            promptVersion="image_features.placeholder.v1",
            modelName=self.model_name,
        )

    @staticmethod
    def _evidence(text: str, fallback: str) -> str:
        compact = " ".join(text.split())
        return compact[:80] if compact else fallback

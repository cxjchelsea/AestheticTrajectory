from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


def build_embedding_text(input_record: AestheticInputResponse, feature: InputFeature | None = None) -> str:
    parts: list[str] = []

    _append(parts, "标题", input_record.title)
    if input_record.type == "text":
        _append(parts, "正文", input_record.content_text)
        _append(parts, "描述", input_record.description)
    else:
        _append(parts, "描述", input_record.description)
        parts.append("当前边界：图片真实分析尚未接入，本轮仅使用用户提供的标题、描述和已抽取 placeholder feature。")

    if feature is not None:
        feature_summary = _feature_summary(feature)
        _append(parts, "特征", feature_summary)
        _append(parts, "证据", "；".join(feature.sample_evidence))

    return "\n".join(part for part in parts if part.strip()).strip()


def _append(parts: list[str], label: str, value: str | None) -> None:
    if value and value.strip():
        parts.append(f"{label}：{value.strip()}")


def _feature_summary(feature: InputFeature) -> str:
    summaries = [
        f"{name}={signal.value}"
        for name, signal in feature.low_level_features.items()
        if signal.evidence
    ]
    return "; ".join(summaries)

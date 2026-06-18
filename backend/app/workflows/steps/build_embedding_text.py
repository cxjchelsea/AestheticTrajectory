from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


def build_embedding_text(input_record: AestheticInputResponse, feature: InputFeature | None = None) -> str:
    parts: list[str] = []

    _append(parts, "标题", input_record.title)
    if input_record.type == "text":
        _append(parts, "正文", input_record.content_text)
        _append(parts, "描述", input_record.description)
    elif input_record.type == "image":
        _append(parts, "描述", input_record.description)
        _append(parts, "文件", input_record.file_url)
        parts.append("当前边界：图片内容理解仍可能使用 placeholder feature；文件 URL 仅作来源记录。")
    elif input_record.type == "music":
        _append(parts, "备注", input_record.content_text)
        _append(parts, "链接", input_record.file_url)
        _append(parts, "描述", input_record.description)
        parts.append("当前边界：未解析音频内容，仅使用音乐元数据参与 embedding。")
    elif input_record.type == "video":
        _append(parts, "备注", input_record.content_text)
        _append(parts, "链接", input_record.file_url)
        _append(parts, "描述", input_record.description)
        parts.append("当前边界：未解析视频内容，仅使用视频元数据参与 embedding。")

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

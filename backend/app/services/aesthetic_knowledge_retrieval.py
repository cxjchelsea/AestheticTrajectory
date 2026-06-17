from app.ai.knowledge.aesthetic_knowledge_base import AESTHETIC_KNOWLEDGE_CHUNKS, KnowledgeChunk
from app.schemas.feature import InputFeature
from app.schemas.knowledge_context import AestheticKnowledgeContext, KnowledgeContextItem

DISCLAIMER = (
    "以下知识参考来自项目审美知识库，只用于解释风格概念，不代表用户偏好证据。"
)
MIN_FEATURE_OVERLAP = 1
DEFAULT_TOP_K = 3


def build_aesthetic_knowledge_context(
    current_features: list[InputFeature],
    top_k: int = DEFAULT_TOP_K,
) -> AestheticKnowledgeContext:
    feature_keys = _feature_keys(current_features)
    if not feature_keys:
        return AestheticKnowledgeContext(
            message="当前输入特征不足，暂时无法匹配审美知识参考。",
            disclaimer=DISCLAIMER,
        )

    ranked = sorted(
        (
            (_overlap_score(chunk, feature_keys), chunk.doc_id, chunk)
            for chunk in AESTHETIC_KNOWLEDGE_CHUNKS
        ),
        key=lambda item: (-item[0], item[1]),
    )
    items: list[KnowledgeContextItem] = []
    for score, _doc_id, chunk in ranked:
        if score < MIN_FEATURE_OVERLAP:
            continue
        matched = sorted(feature_keys & chunk.feature_tags)
        items.append(_to_item(chunk, matched))
        if len(items) >= top_k:
            break

    if not items:
        return AestheticKnowledgeContext(
            message="暂未找到与当前输入足够相关的审美知识参考。",
            disclaimer=DISCLAIMER,
        )

    return AestheticKnowledgeContext(
        items=items,
        summary=_summary(items),
        disclaimer=DISCLAIMER,
    )


def _feature_keys(features: list[InputFeature]) -> set[str]:
    keys: set[str] = set()
    for feature in features:
        for name, signal in feature.low_level_features.items():
            if signal.evidence:
                keys.add(f"{name}={signal.value}")
    return keys


def _overlap_score(chunk: KnowledgeChunk, feature_keys: set[str]) -> int:
    return len(feature_keys & chunk.feature_tags)


def _to_item(chunk: KnowledgeChunk, matched_features: list[str]) -> KnowledgeContextItem:
    matched_text = "、".join(matched_features[:3])
    return KnowledgeContextItem(
        docId=chunk.doc_id,
        title=chunk.title,
        snippet=chunk.snippet,
        matchedFeatures=matched_features,
        sourceRefs=[chunk.doc_id, chunk.source],
        note=f"知识库条目与当前输入在 {matched_text} 等特征上相关，可用于解释风格概念。",
    )


def _summary(items: list[KnowledgeContextItem]) -> str:
    titles = "、".join(item.title for item in items[:2])
    return f"系统从审美知识库中找到 {titles} 等解释参考，用于辅助说明当前输入的结构特征。"

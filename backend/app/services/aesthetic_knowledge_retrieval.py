from app.ai.factory import get_embedding_client
from app.ai.knowledge.aesthetic_knowledge_base import AESTHETIC_KNOWLEDGE_CHUNKS, KnowledgeChunk
from app.schemas.feature import InputFeature
from app.schemas.knowledge_context import (
    AestheticKnowledgeContext,
    KnowledgeContextItem,
    KnowledgeRetrievalMeta,
)
from app.services.knowledge_graph_query import PREDICATE_LABELS

DISCLAIMER = (
    "以下知识参考来自项目审美知识库，只用于解释风格概念，不代表用户偏好证据。"
)
MIN_FEATURE_OVERLAP = 1
DEFAULT_TOP_K = 3


def build_aesthetic_knowledge_context(
    current_features: list[InputFeature],
    *,
    graph_repository=None,
    knowledge_vector_store=None,
    top_k: int = DEFAULT_TOP_K,
) -> AestheticKnowledgeContext:
    feature_keys = _feature_keys(current_features)
    vector_path: str = "not_applicable"
    if not feature_keys:
        return AestheticKnowledgeContext(
            message="当前输入特征不足，暂时无法匹配审美知识参考。",
            disclaimer=DISCLAIMER,
            retrievalMeta=KnowledgeRetrievalMeta(
                tagMatchCount=0,
                graphHitCount=0,
                vectorPath="not_applicable",
                abstentionReason="insufficient_features",
            ),
        )

    ranked = _rank_chunks(feature_keys)
    items: list[KnowledgeContextItem] = []
    for score, _doc_id, chunk in ranked:
        if score < MIN_FEATURE_OVERLAP:
            continue
        matched = sorted(feature_keys & chunk.feature_tags)
        items.append(_to_item(chunk, matched))
        if len(items) >= top_k:
            break

    tag_match_count = len(items)

    vector_error_message = None
    if knowledge_vector_store is not None and settings_chroma_enabled():
        vector_path, items, vector_error_message = _apply_vector_rerank(
            items,
            feature_keys,
            ranked,
            knowledge_vector_store,
            top_k=top_k,
        )

    if not items:
        return AestheticKnowledgeContext(
            message="暂未找到与当前输入足够相关的审美知识参考。",
            disclaimer=DISCLAIMER,
            retrievalMeta=KnowledgeRetrievalMeta(
                tagMatchCount=0,
                graphHitCount=0,
                vectorPath=vector_path if vector_path != "not_applicable" else "skipped",
                abstentionReason="no_tag_overlap",
                vectorErrorMessage=vector_error_message,
            ),
        )

    graph_hit_count = 0
    if graph_repository is not None:
        items, graph_hit_count = _enrich_items_with_graph(items, feature_keys, graph_repository)

    return AestheticKnowledgeContext(
        items=items,
        summary=_summary(items),
        disclaimer=DISCLAIMER,
        retrievalMeta=KnowledgeRetrievalMeta(
            tagMatchCount=tag_match_count,
            graphHitCount=graph_hit_count,
            vectorPath=vector_path,
            abstentionReason=None,
            vectorErrorMessage=vector_error_message,
        ),
    )


def settings_chroma_enabled() -> bool:
    from app.core.config import settings

    return settings.chroma_enabled


def _rank_chunks(feature_keys: set[str]) -> list[tuple[int, str, KnowledgeChunk]]:
    return sorted(
        (
            (_overlap_score(chunk, feature_keys), chunk.doc_id, chunk)
            for chunk in AESTHETIC_KNOWLEDGE_CHUNKS
        ),
        key=lambda item: (-item[0], item[1]),
    )


def _apply_vector_rerank(
    items: list[KnowledgeContextItem],
    feature_keys: set[str],
    ranked: list[tuple[int, str, KnowledgeChunk]],
    knowledge_vector_store,
    *,
    top_k: int,
) -> tuple[str, list[KnowledgeContextItem], str | None]:
    if not items:
        return "skipped", items, None

    try:
        embedding_text = " ".join(sorted(feature_keys))
        embedding_client = get_embedding_client()
        if hasattr(knowledge_vector_store, "ensure_seeded"):
            knowledge_vector_store.ensure_seeded(embedding_client)
        vector = embedding_client.embed(embedding_text)
        result = knowledge_vector_store.query(vector, limit=top_k)
    except Exception as exc:
        return "failed", items, str(exc)

    if result.path == "skipped" or not result.doc_ids:
        return result.path, items, None

    chunk_by_doc = {chunk.doc_id: chunk for chunk in AESTHETIC_KNOWLEDGE_CHUNKS}
    reranked: list[KnowledgeContextItem] = []
    seen_doc_ids: set[str] = set()
    for doc_id in result.doc_ids:
        chunk = chunk_by_doc.get(doc_id)
        if chunk is None:
            continue
        overlap = _overlap_score(chunk, feature_keys)
        if overlap < MIN_FEATURE_OVERLAP:
            continue
        if doc_id in seen_doc_ids:
            continue
        seen_doc_ids.add(doc_id)
        reranked.append(_to_item(chunk, sorted(feature_keys & chunk.feature_tags)))
        if len(reranked) >= top_k:
            break

    if reranked:
        return result.path, reranked, None
    return result.path, items, None


def _enrich_items_with_graph(
    items: list[KnowledgeContextItem],
    feature_keys: set[str],
    graph_repository,
) -> tuple[list[KnowledgeContextItem], int]:
    graph_hits = 0
    enriched: list[KnowledgeContextItem] = []

    for item in items:
        concept_ids: set[str] = set()
        relation_notes: list[str] = []

        for concept in graph_repository.find_concepts_by_doc_id(item.doc_id):
            concept_ids.add(concept.id)

        for concept in graph_repository.find_concepts_by_feature_tags(set(item.matched_features)):
            concept_ids.add(concept.id)

        expanded_concepts, edges = graph_repository.expand_one_hop(concept_ids)
        for concept in expanded_concepts:
            concept_ids.add(concept.id)

        for edge in edges:
            graph_hits += 1
            from_concept = graph_repository.get_concept(edge.from_concept_id)
            to_concept = graph_repository.get_concept(edge.to_concept_id)
            if from_concept is None or to_concept is None:
                continue
            predicate = PREDICATE_LABELS.get(edge.predicate, edge.predicate)
            relation_notes.append(
                f"「{from_concept.label}」与「{to_concept.label}」为{predicate}关系（{edge.source_evidence.note}）。"
            )

        enriched.append(
            item.model_copy(
                update={
                    "related_concept_ids": sorted(concept_ids),
                    "relation_notes": relation_notes[:3],
                }
            )
        )

    return enriched, graph_hits


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
    has_relations = any(item.relation_notes for item in items)
    if has_relations:
        return (
            f"系统从审美知识库中找到 {titles} 等解释参考，"
            "并补充了相关概念关系说明，用于辅助说明当前输入的结构特征。"
        )
    return f"系统从审美知识库中找到 {titles} 等解释参考，用于辅助说明当前输入的结构特征。"

from app.schemas.feature import InputFeature
from app.schemas.interpretation import SimilarityGroup
from app.workflows.steps.similarity import connected_components, cosine_similarity


SIMILARITY_THRESHOLD = 0.82


def cluster_inputs(
    input_ids: list[str],
    features: list[InputFeature],
    embeddings: dict[str, list[float]],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> list[SimilarityGroup]:
    return build_similarity_groups(input_ids, features, embeddings, similarity_threshold)


def build_similarity_groups(
    input_ids: list[str],
    features: list[InputFeature],
    embeddings: dict[str, list[float]],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> list[SimilarityGroup]:
    if len(input_ids) < 3:
        return []

    edges: list[tuple[str, str]] = []
    for left_index, left_id in enumerate(input_ids):
        for right_id in input_ids[left_index + 1 :]:
            if left_id not in embeddings or right_id not in embeddings:
                continue
            if cosine_similarity(embeddings[left_id], embeddings[right_id]) >= similarity_threshold:
                edges.append((left_id, right_id))

    feature_by_input_id = {feature.input_id: feature for feature in features}
    groups: list[SimilarityGroup] = []
    for index, component in enumerate(connected_components(edges), start=1):
        common_features = _common_features(component, feature_by_input_id)
        groups.append(
            SimilarityGroup(
                groupId=f"group_similarity_{index:03d}",
                name=_group_name(common_features),
                inputIds=component,
                commonFeatures=common_features,
                uncertainty=(
                    "该分组基于当前样本的 embedding 相似度和可解释 feature overlap 生成。"
                    "样本数量较少，且当前仍使用 mock embedding，因此它只表示本次输入中的相似结构，"
                    "不代表长期偏好或绝对分类。"
                ),
            )
        )

    return groups


def _common_features(input_ids: list[str], feature_by_input_id: dict[str, InputFeature]) -> list[str]:
    feature_sets: list[set[str]] = []
    key_sets: list[set[str]] = []

    for input_id in input_ids:
        feature = feature_by_input_id.get(input_id)
        if feature is None:
            continue
        feature_sets.append(
            {
                f"{name}:{signal.value}"
                for name, signal in feature.low_level_features.items()
                if signal.evidence
            }
        )
        key_sets.append(
            {
                name
                for name, signal in feature.low_level_features.items()
                if signal.evidence
            }
        )

    if feature_sets:
        exact_overlap = set.intersection(*feature_sets)
        if exact_overlap:
            return sorted(exact_overlap)[:5]

    if key_sets:
        key_overlap = set.intersection(*key_sets)
        if key_overlap:
            return [f"{name}:mixed" for name in sorted(key_overlap)[:5]]

    return ["weak_shared_structure"]


def _group_name(common_features: list[str]) -> str:
    first_feature = common_features[0] if common_features else "weak_shared_structure"
    if first_feature.startswith("saturation:"):
        return "色彩倾向相似组"
    if first_feature.startswith("density:") or first_feature.startswith("narrativeDensity:"):
        return "低密度相似组"
    if first_feature.startswith("subjectDistance:") or first_feature.startswith("imageryType:"):
        return "空间意象相似组"
    return "弱共同结构组"

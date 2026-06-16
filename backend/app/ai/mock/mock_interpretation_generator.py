from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.feature import InputFeature
from app.schemas.report import Insight


class MockInterpretationGenerator:
    def group(self, input_ids: list[str]) -> list[SimilarityGroup]:
        if len(input_ids) < 3:
            return []
        return [
            SimilarityGroup(
                groupId="group_mock_001",
                name="安静低密度组",
                inputIds=input_ids[:3],
                commonFeatures=["low_saturation", "low_density", "person_absent"],
                uncertainty="样本数量较少，该分组只表示本次输入中的相似结构。",
            )
        ]

    def interpret(
        self,
        groups: list[SimilarityGroup],
        features: list[InputFeature],
        input_ids: list[str],
    ) -> list[PossibleInterpretation]:
        evidence_refs = _select_evidence_refs(groups, features, input_ids)
        if not evidence_refs:
            return []

        common_features = _select_common_features(groups, features)
        confidence = _confidence(groups, evidence_refs, input_ids, base=0.72)
        return [
            PossibleInterpretation(
                id="interpretation_mock_001",
                name=_interpretation_name(common_features),
                confidence=confidence,
                evidenceRefs=evidence_refs,
                uncertainty="样本数量仍然较少，该解释只表示当前输入中的一种可能观察，不代表稳定偏好。",
            )
        ]

    def insights(
        self,
        groups: list[SimilarityGroup],
        features: list[InputFeature],
        input_ids: list[str],
    ) -> list[Insight]:
        evidence_refs = _select_evidence_refs(groups, features, input_ids)
        if not evidence_refs:
            return []

        common_features = _select_common_features(groups, features)
        confidence = _confidence(groups, evidence_refs, input_ids, base=0.72)
        feature_phrase = _feature_phrase(common_features)
        return [
            Insight(
                insightId="insight_mock_001",
                title=f"这组样本可能呈现出{feature_phrase}的共同倾向",
                observation=f"当前输入中可以观察到{feature_phrase}等重复出现的结构。",
                evidenceRefs=evidence_refs,
                interpretation=f"在这组样本中，这可能表示你倾向于关注{feature_phrase}带来的审美感受。",
                uncertainty="它不是人格诊断或心理评估，只是对本次样本的审美结构观察。",
                confidence=confidence,
            )
        ]


def _select_evidence_refs(
    groups: list[SimilarityGroup],
    features: list[InputFeature],
    input_ids: list[str],
) -> list[str]:
    for group in groups:
        if group.input_ids:
            return group.input_ids[:3]

    evidence_counts = sorted(
        (
            (
                feature.input_id,
                sum(len(signal.evidence) for signal in feature.low_level_features.values())
                + len(feature.sample_evidence),
            )
            for feature in features
            if feature.input_id in input_ids
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    if evidence_counts:
        return [input_id for input_id, count in evidence_counts[:3] if count > 0]

    return input_ids[:1]


def _select_common_features(groups: list[SimilarityGroup], features: list[InputFeature]) -> list[str]:
    for group in groups:
        strong_features = [
            feature
            for feature in group.common_features
            if feature != "weak_shared_structure"
        ]
        if strong_features:
            return strong_features[:3]

    feature_scores: dict[str, int] = {}
    for feature in features:
        for name, signal in feature.low_level_features.items():
            if signal.evidence:
                feature_scores[f"{name}:{signal.value}"] = feature_scores.get(f"{name}:{signal.value}", 0) + 1

    ranked_features = sorted(feature_scores.items(), key=lambda item: item[1], reverse=True)
    return [feature for feature, _count in ranked_features[:3]] or ["weak_shared_structure"]


def _confidence(
    groups: list[SimilarityGroup],
    evidence_refs: list[str],
    input_ids: list[str],
    base: float,
) -> float:
    confidence = base
    if len(input_ids) < 3:
        confidence = min(confidence, 0.55)
    if not groups:
        confidence = min(confidence, 0.62)
    if any("weak_shared_structure" in group.common_features for group in groups):
        confidence = min(confidence, 0.62)
    if len(evidence_refs) < 2:
        confidence = min(confidence, 0.60)
    return confidence


def _interpretation_name(common_features: list[str]) -> str:
    phrase = _feature_phrase(common_features)
    if phrase == "弱共同结构":
        return "当前样本中的弱共同结构"
    return f"{phrase}相关的审美倾向"


def _feature_phrase(common_features: list[str]) -> str:
    labels = [_feature_label(feature) for feature in common_features[:3]]
    return "、".join(labels) if labels else "弱共同结构"


def _feature_label(feature: str) -> str:
    if feature == "weak_shared_structure":
        return "弱共同结构"
    if ":" not in feature:
        return feature
    name, value = feature.split(":", 1)
    return f"{name}={value}"

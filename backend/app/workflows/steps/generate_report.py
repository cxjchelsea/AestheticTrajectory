from app.schemas.feature import InputFeature
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.report import Insight, ReportResponse


def generate_report(
    report_id: str,
    features: list[InputFeature],
    groups: list[SimilarityGroup],
    interpretations: list[PossibleInterpretation],
    insights: list[Insight],
) -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title="近期审美观察报告",
        summary=_build_summary(features, groups, interpretations),
        lowLevelFeatures=features,
        similarityGroups=groups,
        possibleInterpretations=interpretations,
        insights=insights,
        disclaimer="这是一份基于当前输入的审美观察，不是人格诊断、心理评估或长期画像。",
    )


def _build_summary(
    features: list[InputFeature],
    groups: list[SimilarityGroup],
    interpretations: list[PossibleInterpretation],
) -> str:
    common_features = _group_common_features(groups) or _ranked_feature_labels(features)
    if not common_features:
        return "当前样本中的共同结构还不稳定。系统仅整理已观察到的底层特征，并等待更多输入或反馈来确认这些倾向是否成立。"

    feature_text = "、".join(common_features[:3])
    interpretation_text = ""
    if interpretations:
        interpretation_text = f" 其中一个可能解释是“{interpretations[0].name}”。"

    return (
        f"这组输入整体呈现出{feature_text}的倾向。"
        "系统只把这些视为本次样本中的可观察结构，而不是人格诊断或长期画像。"
        f"{interpretation_text}"
    )


def _group_common_features(groups: list[SimilarityGroup]) -> list[str]:
    for group in groups:
        strong_features = [
            _feature_label(feature)
            for feature in group.common_features
            if feature != "weak_shared_structure"
        ]
        if strong_features:
            return strong_features
    return []


def _ranked_feature_labels(features: list[InputFeature]) -> list[str]:
    feature_scores: dict[str, int] = {}
    for feature in features:
        for name, signal in feature.low_level_features.items():
            if signal.evidence:
                key = f"{name}:{signal.value}"
                feature_scores[key] = feature_scores.get(key, 0) + 1

    return [
        _feature_label(feature)
        for feature, _count in sorted(feature_scores.items(), key=lambda item: item[1], reverse=True)
    ]


def _feature_label(feature: str) -> str:
    if ":" not in feature:
        return feature
    name, value = feature.split(":", 1)
    return f"{name}={value}"

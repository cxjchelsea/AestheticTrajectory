from app.schemas.feature import InputFeature
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.history_context import HistoryContextItem, PersonalHistoryContext
from app.schemas.report import ReportResponse

DISCLAIMER = (
    "以下历史参考来自过往报告和用户反馈，用于辅助理解当前输入，不是人格、心理或能力判断。"
)


def build_personal_history_context(
    current_report_id: str | None,
    current_features: list[InputFeature],
    historical_reports: list[ReportResponse],
    feedback: list[InsightFeedbackResponse],
) -> PersonalHistoryContext:
    prior_reports = [report for report in historical_reports if report.report_id != current_report_id]
    if not prior_reports:
        return PersonalHistoryContext(
            message="暂无可参考的历史报告。",
            disclaimer=DISCLAIMER,
        )

    current_feature_keys = _feature_keys(current_features)
    items: list[HistoryContextItem] = []

    for report in prior_reports[:5]:
        matched = sorted(current_feature_keys & _feature_keys(report.low_level_features))
        if not matched:
            continue
        matched_text = "、".join(matched[:3])
        items.append(
            HistoryContextItem(
                sourceType="report",
                sourceId=report.report_id,
                sourceRefs=[report.report_id],
                direction="neutral",
                matchedFeatures=matched[:5],
                label=report.title,
                note=f"历史报告与当前输入在 {matched_text} 等特征上存在重叠。",
            )
        )

    feedback_by_insight = {item.insight_id: item for item in feedback}
    for report in prior_reports:
        for insight in report.insights:
            item = feedback_by_insight.get(insight.insight_id)
            if item is None:
                continue

            direction, note = _feedback_context(insight.title, item.rating)
            if direction is None:
                continue

            items.append(
                HistoryContextItem(
                    sourceType="feedback",
                    sourceId=item.id,
                    sourceRefs=[report.report_id, insight.insight_id],
                    direction=direction,
                    label=insight.title,
                    note=note,
                )
            )

    items = _dedupe_items(items)[:8]
    if not items:
        return PersonalHistoryContext(
            message="暂未找到与当前输入足够相关的历史参考。",
            disclaimer=DISCLAIMER,
        )

    return PersonalHistoryContext(
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


def _feedback_context(label: str, rating: str) -> tuple[str | None, str | None]:
    if rating == "not_me":
        return "negative", f"用户曾否定“{label}”这一解释方向。"
    if rating == "unsure":
        return "neutral", f"用户对“{label}”曾表示不确定。"
    if rating in {"somewhat_me", "very_me"}:
        return "positive", f"用户曾认可“{label}”这一解释方向。"
    return None, None


def _dedupe_items(items: list[HistoryContextItem]) -> list[HistoryContextItem]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[HistoryContextItem] = []
    for item in items:
        key = (item.source_type, item.source_id, item.direction)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _summary(items: list[HistoryContextItem]) -> str:
    report_items = [item for item in items if item.source_type == "report"]
    positive_items = [item for item in items if item.direction == "positive"]
    negative_items = [item for item in items if item.direction == "negative"]

    if report_items:
        labels = "、".join(item.matched_features[0] for item in report_items[:2] if item.matched_features)
        if labels:
            return f"系统从历史报告中找到与当前输入相关的 {labels} 等结构参考。"

    if positive_items:
        labels = "、".join(item.label for item in positive_items[:2])
        return f"历史反馈显示用户曾认可 {labels} 等解释方向。"

    if negative_items:
        labels = "、".join(item.label for item in negative_items[:2])
        return f"历史反馈显示用户曾否定 {labels} 等解释方向，当前报告不会将其作为正向偏好。"

    return "系统找到了少量历史参考，用于辅助理解当前输入。"

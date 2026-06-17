from collections import Counter

from app.schemas.report import ReportResponse
from app.schemas.report_comparison import (
    ComparisonReportRef,
    ReportComparisonResponse,
    ReportFeatureChange,
    ReportInterpretationChange,
)

DISCLAIMER = "这只是最近两次输入之间的审美结构对比，不是人格、心理或能力判断。"


def build_latest_report_comparison(user_id: str, reports: list[ReportResponse]) -> ReportComparisonResponse:
    if len(reports) < 2:
        return ReportComparisonResponse(
            userId=user_id,
            message="历史报告不足两份，暂时无法生成最近变化说明。",
            disclaimer=DISCLAIMER,
        )

    current, previous = reports[0], reports[1]
    feature_changes = _feature_changes(previous, current)
    interpretation_changes = _interpretation_changes(previous, current)
    summary = _summary(feature_changes, interpretation_changes)

    return ReportComparisonResponse(
        userId=user_id,
        previousReport=_report_ref(previous),
        currentReport=_report_ref(current),
        featureChanges=feature_changes,
        interpretationChanges=interpretation_changes,
        summary=summary,
        message=None,
        disclaimer=DISCLAIMER,
    )


def _report_ref(report: ReportResponse) -> ComparisonReportRef:
    return ComparisonReportRef(
        reportId=report.report_id,
        title=report.title,
        summary=report.summary,
        createdAt=None,
    )


def _feature_changes(previous: ReportResponse, current: ReportResponse) -> list[ReportFeatureChange]:
    previous_counts = _feature_counts(previous)
    current_counts = _feature_counts(current)
    labels = sorted(set(previous_counts) | set(current_counts))
    changes: list[ReportFeatureChange] = []

    for label in labels:
        previous_count = previous_counts.get(label, 0)
        current_count = current_counts.get(label, 0)
        if previous_count == current_count == 0:
            continue

        change_type = _feature_change_type(previous_count, current_count)
        if change_type is None:
            continue

        changes.append(
            ReportFeatureChange(
                changeType=change_type,
                label=label,
                previousCount=previous_count,
                currentCount=current_count,
                evidenceRefs=[previous.report_id, current.report_id],
                note=_feature_note(label, change_type),
            )
        )

    return changes[:8]


def _feature_counts(report: ReportResponse) -> Counter[str]:
    counts: Counter[str] = Counter()
    for feature in report.low_level_features:
        for name, signal in feature.low_level_features.items():
            counts[f"{name}={signal.value}"] += 1
    return counts


def _feature_change_type(previous_count: int, current_count: int) -> str | None:
    if previous_count == 0 and current_count > 0:
        return "new"
    if previous_count > 0 and current_count == 0:
        return "decreased"
    if current_count > previous_count:
        return "increased"
    if current_count < previous_count:
        return "decreased"
    if current_count > 0:
        return "repeated"
    return None


def _feature_note(label: str, change_type: str) -> str:
    labels = {
        "new": f"这次输入中新出现了 {label}。",
        "increased": f"这次输入中 {label} 出现得更明显。",
        "decreased": f"这次输入中 {label} 相比上一次减弱或未继续出现。",
        "repeated": f"最近两次输入中都能看到 {label}。",
    }
    return labels[change_type]


def _interpretation_changes(previous: ReportResponse, current: ReportResponse) -> list[ReportInterpretationChange]:
    previous_labels = set(_interpretation_labels(previous))
    current_labels = set(_interpretation_labels(current))
    changes: list[ReportInterpretationChange] = []

    for label in sorted(current_labels - previous_labels):
        changes.append(
            ReportInterpretationChange(
                changeType="new",
                label=label,
                evidenceRefs=[current.report_id],
                note=f"这次报告中新出现了“{label}”这一解释方向。",
            )
        )
    for label in sorted(previous_labels & current_labels):
        changes.append(
            ReportInterpretationChange(
                changeType="repeated",
                label=label,
                evidenceRefs=[previous.report_id, current.report_id],
                note=f"最近两次报告都保留了“{label}”这一解释方向。",
            )
        )
    for label in sorted(previous_labels - current_labels):
        changes.append(
            ReportInterpretationChange(
                changeType="decreased",
                label=label,
                evidenceRefs=[previous.report_id],
                note=f"这次报告中没有继续强化“{label}”这一解释方向。",
            )
        )
    return changes[:6]


def _interpretation_labels(report: ReportResponse) -> list[str]:
    labels = [item.name for item in report.possible_interpretations]
    labels.extend(insight.title for insight in report.insights)
    return labels


def _summary(
    feature_changes: list[ReportFeatureChange],
    interpretation_changes: list[ReportInterpretationChange],
) -> str:
    directional = [
        change
        for change in feature_changes
        if change.change_type in {"new", "increased", "decreased"}
    ]
    if directional:
        labels = "、".join(change.label for change in directional[:3])
        return f"最近两次输入相比，系统观察到 {labels} 等可见特征方向发生了变化。"

    if interpretation_changes:
        labels = "、".join(change.label for change in interpretation_changes[:2])
        return f"最近两次报告相比，解释方向主要围绕 {labels} 延续或调整。"

    return "最近两次报告之间暂未观察到足够明确的结构变化。"

from datetime import datetime

from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.report import ReportResponse
from app.schemas.timeline import TimelineEventDraft, TimelineEvidence
from app.services.report_comparison import build_latest_report_comparison


def build_timeline_events_for_report(
    user_id: str,
    report: ReportResponse,
    occurred_at: datetime,
    recent_reports: list[ReportResponse],
) -> list[TimelineEventDraft]:
    drafts: list[TimelineEventDraft] = []
    drafts.append(_report_completed_event(user_id, report, occurred_at))

    if len(recent_reports) >= 2:
        current, previous = recent_reports[0], recent_reports[1]
        comparison = build_latest_report_comparison(user_id, [current, previous])
        drafts.extend(_comparison_events(user_id, comparison, occurred_at, len(recent_reports)))

    drafts.extend(_stable_preference_events(user_id, recent_reports, occurred_at))
    return drafts


def build_feedback_decline_event(
    user_id: str,
    feedback: InsightFeedbackResponse,
    insight_title: str,
    report_id: str | None,
    occurred_at: datetime,
) -> TimelineEventDraft | None:
    if feedback.rating != "not_me":
        return None

    related_report_ids = [report_id] if report_id else []
    return TimelineEventDraft(
        userId=user_id,
        eventType="interpretation_decline",
        title=insight_title,
        description="用户反馈表示这条解释方向不太像自己。",
        relatedReportIds=related_report_ids,
        relatedInsightIds=[feedback.insight_id],
        relatedFeedbackIds=[feedback.id],
        evidence=TimelineEvidence(
            evidenceRefs=related_report_ids + [feedback.insight_id, feedback.id],
            insightIds=[feedback.insight_id],
            feedbackIds=[feedback.id],
            note="来自 not_me 反馈",
            dedupeKey=f"{user_id}:feedback:{feedback.insight_id}:interpretation_decline",
        ),
        occurredAt=occurred_at,
    )


def _report_completed_event(
    user_id: str,
    report: ReportResponse,
    occurred_at: datetime,
) -> TimelineEventDraft:
    return TimelineEventDraft(
        userId=user_id,
        eventType="report_completed",
        title="完成一次审美分析",
        description=report.summary,
        relatedReportIds=[report.report_id],
        evidence=TimelineEvidence(
            evidenceRefs=[report.report_id],
            note="分析任务完成并保存报告",
            dedupeKey=f"{user_id}:{report.report_id}:report_completed",
        ),
        occurredAt=occurred_at,
    )


def _comparison_events(
    user_id: str,
    comparison,
    occurred_at: datetime,
    total_reports: int,
) -> list[TimelineEventDraft]:
    if comparison.current_report is None or comparison.previous_report is None:
        return []

    drafts: list[TimelineEventDraft] = []
    current_id = comparison.current_report.report_id
    previous_id = comparison.previous_report.report_id
    comparison_ref = f"{previous_id}->{current_id}"

    for change in comparison.feature_changes:
        if change.change_type in {"new", "increased"}:
            event_type = "feature_shift"
            title = f"特征变化：{change.label}"
        elif change.change_type == "decreased":
            event_type = "feature_shift"
            title = f"特征减弱：{change.label}"
        elif change.change_type == "repeated" and total_reports >= 3:
            event_type = "stable_preference"
            title = f"稳定复现：{change.label}"
        else:
            continue

        drafts.append(
            TimelineEventDraft(
                userId=user_id,
                eventType=event_type,
                title=title,
                description=change.note,
                relatedReportIds=[previous_id, current_id],
                evidence=TimelineEvidence(
                    evidenceRefs=change.evidence_refs,
                    comparisonRef=comparison_ref,
                    featureKeys=[change.label],
                    note=change.note,
                    dedupeKey=f"{user_id}:{comparison_ref}:feature:{change.label}:{change.change_type}",
                ),
                occurredAt=occurred_at,
            )
        )

    for change in comparison.interpretation_changes:
        if change.change_type == "new":
            event_type = "new_interpretation"
            title = f"新解释方向：{change.label}"
        elif change.change_type == "decreased":
            event_type = "interpretation_decline"
            title = f"解释减弱：{change.label}"
        elif change.change_type == "repeated" and total_reports >= 3:
            event_type = "stable_preference"
            title = f"稳定主题：{change.label}"
        else:
            continue

        drafts.append(
            TimelineEventDraft(
                userId=user_id,
                eventType=event_type,
                title=title,
                description=change.note,
                relatedReportIds=change.evidence_refs,
                evidence=TimelineEvidence(
                    evidenceRefs=change.evidence_refs,
                    comparisonRef=comparison_ref,
                    note=change.note,
                    dedupeKey=f"{user_id}:{comparison_ref}:interpretation:{change.label}:{change.change_type}",
                ),
                occurredAt=occurred_at,
            )
        )

    return drafts


def _stable_preference_events(
    user_id: str,
    reports: list[ReportResponse],
    occurred_at: datetime,
) -> list[TimelineEventDraft]:
    if len(reports) < 3:
        return []

    current = reports[0]
    feature_counts: dict[str, int] = {}
    for report in reports:
        for feature in report.low_level_features:
            for name, signal in feature.low_level_features.items():
                key = f"{name}={signal.value}"
                feature_counts[key] = feature_counts.get(key, 0) + 1

    drafts: list[TimelineEventDraft] = []
    for label, count in sorted(feature_counts.items()):
        if count < 3:
            continue
        drafts.append(
            TimelineEventDraft(
                userId=user_id,
                eventType="stable_preference",
                title=f"跨多次分析的稳定特征：{label}",
                description=f"该特征方向在最近 {count} 次分析中出现。",
                relatedReportIds=[report.report_id for report in reports[:count]],
                evidence=TimelineEvidence(
                    evidenceRefs=[report.report_id for report in reports[:count]],
                    featureKeys=[label],
                    note="跨报告统计",
                    dedupeKey=f"{user_id}:stable:{label}",
                ),
                occurredAt=occurred_at,
            )
        )
    return drafts[:5]

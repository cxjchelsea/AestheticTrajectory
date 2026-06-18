from datetime import datetime, timedelta

from app.repositories.timeline_repository import TIMELINE_DISCLAIMER
from app.schemas.common import utc_now
from app.schemas.timeline import TimelineSummaryHighlight, TimelineSummaryPeriod, TimelineSummaryResponse


def build_timeline_summary(
    user_id: str,
    period: TimelineSummaryPeriod,
    timeline_repository,
    report_repository,
) -> TimelineSummaryResponse:
    now = utc_now()
    window_start = now - (timedelta(days=7) if period == "week" else timedelta(days=30))
    timeline = timeline_repository.list_by_user(
        user_id,
        limit=200,
        offset=0,
        occurred_from=window_start,
        occurred_to=now,
    )
    report_count = sum(1 for event in timeline.events if event.event_type == "report_completed")

    if not timeline.events:
        return TimelineSummaryResponse(
            userId=user_id,
            period=period,
            summaryText="",
            eventCount=0,
            reportCount=report_count,
            highlights=[],
            message=f"最近{'一周' if period == 'week' else '一月'}还没有足够的时间轴事件。",
            disclaimer=TIMELINE_DISCLAIMER,
        )

    highlights = [
        TimelineSummaryHighlight(
            eventType=event.event_type,
            title=event.title,
            occurredAt=event.occurred_at,
            evidenceRefs=event.evidence.evidence_refs,
        )
        for event in timeline.events[:5]
    ]
    shift_count = sum(1 for event in timeline.events if event.event_type in {"feature_shift", "style_shift"})
    stable_count = sum(1 for event in timeline.events if event.event_type == "stable_preference")
    decline_count = sum(1 for event in timeline.events if event.event_type == "interpretation_decline")

    parts: list[str] = []
    if report_count:
        parts.append(f"最近{'一周' if period == 'week' else '一月'}共完成 {report_count} 次分析")
    parts.append(f"记录 {timeline.total} 条时间轴事件")
    if shift_count:
        parts.append(f"其中 {shift_count} 条体现特征或解释方向变化")
    if stable_count:
        parts.append(f"{stable_count} 条体现稳定复现")
    if decline_count:
        parts.append(f"{decline_count} 条与用户否定或减弱信号相关")

    return TimelineSummaryResponse(
        userId=user_id,
        period=period,
        summaryText="；".join(parts) + "。",
        eventCount=timeline.total,
        reportCount=report_count,
        highlights=highlights,
        message=None,
        disclaimer=TIMELINE_DISCLAIMER,
    )

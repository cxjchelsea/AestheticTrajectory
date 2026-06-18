from dataclasses import dataclass
from datetime import datetime

from app.schemas.common import utc_now
from app.schemas.report import ReportResponse
from app.schemas.timeline import TimelineEvent
from app.services.timeline_builder import build_timeline_events_for_report


@dataclass
class UpdateTrajectoryResult:
    events: list[TimelineEvent]
    status: str
    error_message: str | None = None


def update_trajectory(
    user_id: str,
    report: ReportResponse,
    report_repository,
    timeline_repository,
    occurred_at: datetime | None = None,
) -> UpdateTrajectoryResult:
    try:
        recent_reports = report_repository.list_recent_by_user(user_id, limit=10)
        if not recent_reports or recent_reports[0].report_id != report.report_id:
            recent_reports = [report, *recent_reports]
        else:
            recent_reports = recent_reports

        drafts = build_timeline_events_for_report(
            user_id,
            report,
            occurred_at or utc_now(),
            recent_reports,
        )
        events = timeline_repository.append_events(drafts)
        return UpdateTrajectoryResult(events=events, status="success")
    except Exception as exc:
        return UpdateTrajectoryResult(events=[], status="failed", error_message=str(exc))

from app.services.timeline_summary import build_timeline_summary


class TimelineService:
    def __init__(self, timeline_repository, report_repository) -> None:
        self.timeline_repository = timeline_repository
        self.report_repository = report_repository

    def list_timeline(self, user_id: str, *, limit: int = 50, offset: int = 0):
        return self.timeline_repository.list_by_user(user_id, limit=limit, offset=offset)

    def get_summary(self, user_id: str, period: str):
        return build_timeline_summary(user_id, period, self.timeline_repository, self.report_repository)

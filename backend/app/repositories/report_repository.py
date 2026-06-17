from app.repositories.memory_store import MemoryStore
from app.schemas.common import utc_now
from app.schemas.report import ReportHistoryResponse, ReportResponse, ReportSummary


class ReportRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, report: ReportResponse, user_id: str | None = None, job_id: str | None = None) -> ReportResponse:
        self.store.reports[report.report_id] = report
        self.store.report_metadata[report.report_id] = {
            "user_id": user_id,
            "job_id": job_id,
            "created_at": utc_now(),
        }
        return report

    def get(self, report_id: str) -> ReportResponse | None:
        return self.store.reports.get(report_id)

    def get_job_id(self, report_id: str) -> str | None:
        metadata = self.store.report_metadata.get(report_id)
        if metadata is None:
            return None
        job_id = metadata.get("job_id")
        return job_id if isinstance(job_id, str) else None

    def get_user_id(self, report_id: str) -> str | None:
        metadata = self.store.report_metadata.get(report_id)
        if metadata is None:
            return None
        user_id = metadata.get("user_id")
        return user_id if isinstance(user_id, str) else None

    def list_by_user(self, user_id: str, limit: int, offset: int) -> ReportHistoryResponse:
        summaries: list[ReportSummary] = []
        for report_id, report in self.store.reports.items():
            metadata = self.store.report_metadata.get(report_id, {})
            if metadata.get("user_id") != user_id:
                continue
            summaries.append(
                ReportSummary(
                    reportId=report.report_id,
                    jobId=metadata.get("job_id"),
                    title=report.title,
                    summary=report.summary,
                    inputCount=len(report.low_level_features),
                    createdAt=metadata.get("created_at") or utc_now(),
                )
            )

        summaries.sort(key=lambda item: (item.created_at, item.report_id), reverse=True)
        total = len(summaries)
        return ReportHistoryResponse(
            reports=summaries[offset : offset + limit],
            total=total,
            limit=limit,
            offset=offset,
        )

    def list_recent_by_user(self, user_id: str, limit: int) -> list[ReportResponse]:
        rows: list[tuple[object, str, ReportResponse]] = []
        for report_id, report in self.store.reports.items():
            metadata = self.store.report_metadata.get(report_id, {})
            if metadata.get("user_id") != user_id:
                continue
            rows.append((metadata.get("created_at") or utc_now(), report_id, report))

        rows.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [report for _, _, report in rows[:limit]]

from dataclasses import dataclass
from datetime import datetime

from app.schemas.common import utc_now


@dataclass(frozen=True)
class AnalysisLogEntry:
    job_id: str
    step_id: str
    status: str
    created_at: datetime


def log_step(job_id: str, step_id: str, status: str) -> AnalysisLogEntry:
    return AnalysisLogEntry(job_id=job_id, step_id=step_id, status=status, created_at=utc_now())

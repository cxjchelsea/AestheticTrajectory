from collections.abc import Callable
from time import perf_counter

from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.common import new_id, utc_now


def record_step(
    log_repository,
    job_id: str,
    step_id: str,
    operation: Callable[[], object],
    model_name: str | None = None,
    prompt_version: str | None = None,
) -> object:
    started_at = utc_now()
    start = perf_counter()
    try:
        result = operation()
    except Exception as error:
        finished_at = utc_now()
        log_repository.save(
            AnalysisLogRecord(
                id=new_id("log"),
                jobId=job_id,
                stepId=step_id,
                status="failed",
                modelName=model_name,
                promptVersion=prompt_version,
                latencyMs=_latency_ms(start),
                errorType=type(error).__name__,
                errorMessage=str(error),
                startedAt=started_at,
                finishedAt=finished_at,
                createdAt=finished_at,
            )
        )
        raise

    finished_at = utc_now()
    log_repository.save(
        AnalysisLogRecord(
            id=new_id("log"),
            jobId=job_id,
            stepId=step_id,
            status="success",
            modelName=model_name,
            promptVersion=prompt_version,
            latencyMs=_latency_ms(start),
            errorType=None,
            errorMessage=None,
            startedAt=started_at,
            finishedAt=finished_at,
            createdAt=finished_at,
        )
    )
    return result


def _latency_ms(start: float) -> int:
    return max(0, int((perf_counter() - start) * 1000))

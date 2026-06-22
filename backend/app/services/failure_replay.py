from collections import defaultdict

from app.schemas.analysis_debug import FallbackEvent
from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.evaluation_maturity import (
    FAILURE_REPLAY_DISCLAIMER,
    FailureReplayFallback,
    FailureReplayResponse,
    FailureReplayStep,
)


def build_failure_replay(
    job_id: str,
    job_status: str,
    logs: list[AnalysisLogRecord],
    fallback_events: list[FallbackEvent],
) -> FailureReplayResponse:
    ordered_logs = sorted(
        logs,
        key=lambda log: log.started_at or log.created_at,
    )
    fallbacks_by_step: dict[str, list[FallbackEvent]] = defaultdict(list)
    for event in fallback_events:
        fallbacks_by_step[event.step_id].append(event)

    steps: list[FailureReplayStep] = []
    for log in ordered_logs:
        step_fallbacks = [
            FailureReplayFallback(
                fallbackType=event.fallback_type,
                originalError=event.original_error,
                fallbackAction=event.fallback_action,
                severity=event.severity,
                developerMessage=event.developer_message,
            )
            for event in fallbacks_by_step.get(log.step_id, [])
        ]
        steps.append(
            FailureReplayStep(
                stepId=log.step_id,
                status=log.status,
                errorType=log.error_type,
                errorMessage=log.error_message,
                latencyMs=log.latency_ms,
                fallbacks=step_fallbacks,
                developerSummary=_developer_summary(log, step_fallbacks),
            )
        )

    failed = job_status == "failed" or any(log.status == "failed" for log in ordered_logs)
    message = None
    if not failed:
        message = "该 job 未记录失败步骤；以下为 workflow 只读回放。"

    return FailureReplayResponse(
        jobId=job_id,
        failed=failed,
        steps=steps,
        message=message,
        replayDisclaimer=FAILURE_REPLAY_DISCLAIMER,
    )


def _developer_summary(
    log: AnalysisLogRecord,
    fallbacks: list[FailureReplayFallback],
) -> str:
    if log.status == "failed":
        error_type = log.error_type or "UnknownError"
        error_message = log.error_message or "No error message recorded."
        return f"Step failed with {error_type}: {error_message}"

    if fallbacks:
        return f"Step completed with {len(fallbacks)} fallback event(s)."

    return f"Step completed with status {log.status}."

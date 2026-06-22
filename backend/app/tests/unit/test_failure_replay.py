from app.schemas.analysis_debug import FallbackEvent
from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.common import utc_now
from app.services.failure_replay import build_failure_replay


def test_failure_replay_marks_failed_job() -> None:
    now = utc_now()
    logs = [
        AnalysisLogRecord(
            id="log_success",
            jobId="job_failed",
            stepId="extract_features",
            status="success",
            modelName=None,
            promptVersion=None,
            latencyMs=10,
            errorType=None,
            errorMessage=None,
            startedAt=now,
            finishedAt=now,
            createdAt=now,
        ),
        AnalysisLogRecord(
            id="log_failed",
            jobId="job_failed",
            stepId="generate_embeddings",
            status="failed",
            modelName=None,
            promptVersion=None,
            latencyMs=5,
            errorType="ValueError",
            errorMessage="Embedding vector dimension does not match client vector_dimension",
            startedAt=now,
            finishedAt=now,
            createdAt=now,
        ),
    ]
    fallbacks = [
        FallbackEvent(
            id="fallback_001",
            jobId="job_failed",
            stepId="write_vectors",
            fallbackType="chroma_upsert_skipped",
            originalError="CHROMA_ENABLED=false",
            fallbackAction="Persisted embedding metadata without remote vector upsert",
            severity="info",
            userVisible=False,
            developerMessage="Chroma write skipped",
            createdAt=now,
        )
    ]

    replay = build_failure_replay("job_failed", "failed", logs, fallbacks)

    assert replay.failed is True
    assert replay.steps[1].status == "failed"
    assert replay.steps[1].error_type == "ValueError"
    assert "只读回放" in replay.replay_disclaimer


def test_failure_replay_success_job_has_message() -> None:
    now = utc_now()
    logs = [
        AnalysisLogRecord(
            id="log_success",
            jobId="job_success",
            stepId="extract_features",
            status="success",
            modelName=None,
            promptVersion=None,
            latencyMs=10,
            errorType=None,
            errorMessage=None,
            startedAt=now,
            finishedAt=now,
            createdAt=now,
        )
    ]

    replay = build_failure_replay("job_success", "completed", logs, [])

    assert replay.failed is False
    assert replay.message
    assert replay.steps[0].developer_summary.startswith("Step completed")

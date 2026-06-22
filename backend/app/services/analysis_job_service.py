from app.core.config import settings
from app.schemas.analysis_job import AnalysisJobResponse, CreateAnalysisJobRequest
from app.schemas.analysis_debug import (
    AnalysisJobDebugResponse,
    BoundaryWarning,
    FallbackEvent,
    MockUsageRecord,
)
from app.schemas.common import new_id, utc_now
from app.services.failure_replay import build_failure_replay
from app.services.grouping_stability import build_grouping_stability_trace
from app.services.observability_trace import build_debug_traces
from app.services.schema_validation_summary import build_schema_validation_records
from app.vector_store.input_vector_store import ChromaWriteResult
from app.workflows.aesthetic_analysis_v1 import run_mock_aesthetic_analysis


class AnalysisJobService:
    def __init__(self, job_repository, input_repository, workflow_persistence) -> None:
        self.job_repository = job_repository
        self.input_repository = input_repository
        self.workflow_persistence = workflow_persistence

    def create_job(self, request: CreateAnalysisJobRequest) -> AnalysisJobResponse:
        now = utc_now()
        job = AnalysisJobResponse(
            id=new_id("job"),
            userId="user_anonymous",
            status="created",
            inputCount=len(request.input_ids),
            errorMessage=None,
            reportId=None,
            createdAt=now,
            startedAt=now,
            finishedAt=None,
        )
        self.job_repository.save(job)
        inputs = self.input_repository.get_many(request.input_ids)
        result = run_mock_aesthetic_analysis(job, inputs, self.workflow_persistence)
        return self.job_repository.save(result)

    def get_failure_replay(self, job_id: str):
        job = self.job_repository.get(job_id)
        if job is None:
            return None
        logs = sorted(
            self.workflow_persistence.analysis_log_repository.get_for_job(job_id),
            key=lambda log: log.created_at,
        )
        chroma_result = None
        if self.workflow_persistence.chroma_write_results is not None:
            chroma_result = self.workflow_persistence.chroma_write_results.get(job_id)
        fallback_events = _chroma_fallback_events(job.id, chroma_result)
        return build_failure_replay(job.id, job.status, logs, fallback_events)

    def get_job(self, job_id: str) -> AnalysisJobResponse | None:
        return self.job_repository.get(job_id)

    def get_debug(self, job_id: str) -> AnalysisJobDebugResponse | None:
        job = self.job_repository.get(job_id)
        if job is None:
            return None

        logs = sorted(
            self.workflow_persistence.analysis_log_repository.get_for_job(job_id),
            key=lambda log: log.created_at,
        )
        schema_validation = build_schema_validation_records(logs)
        report = None
        if job.report_id is not None:
            report = self.workflow_persistence.report_repository.get(job.report_id)
        retrieval_trace, retrieval_items, context_assembly_trace, evaluation_trace = build_debug_traces(
            report,
            logs,
            schema_validation,
        )
        chroma_result = None
        if self.workflow_persistence.chroma_write_results is not None:
            chroma_result = self.workflow_persistence.chroma_write_results.get(job_id)
        fallback_events = _chroma_fallback_events(job.id, chroma_result)
        grouping_inputs = []
        if report is not None:
            input_ids = [feature.input_id for feature in report.low_level_features]
            grouping_inputs = self.input_repository.get_many(input_ids)
        grouping_stability_trace = build_grouping_stability_trace(report, grouping_inputs)
        failure_replay = build_failure_replay(job.id, job.status, logs, fallback_events)
        return AnalysisJobDebugResponse(
            jobId=job.id,
            status=job.status,
            workflowTrace=logs,
            fallbackEvents=fallback_events,
            mockUsage=_mock_usage(),
            schemaValidation=schema_validation,
            boundaryWarnings=_boundary_warnings(logs, chroma_result),
            retrievalTrace=retrieval_trace,
            retrievalItems=retrieval_items,
            contextAssemblyTrace=context_assembly_trace,
            evaluationTrace=evaluation_trace,
            groupingStabilityTrace=grouping_stability_trace,
            failureReplay=failure_replay,
        )


def _mock_usage() -> list[MockUsageRecord]:
    embedding_runtime = settings.embedding_runtime
    embedding_records = [
        MockUsageRecord(
            component="MockFeatureExtractor",
            status="enabled",
            devOnly=True,
            developerMessage="V4-A still uses mock or heuristic feature extraction; real vision/audio parsing is not enabled.",
        ),
        MockUsageRecord(
            component="MockInterpretationGenerator",
            status="enabled",
            devOnly=True,
            developerMessage="Interpretations are generated by the local mock workflow and must not be treated as validated LLM output.",
        ),
    ]
    if embedding_runtime == "openai" and settings.openai_api_key:
        embedding_records.insert(
            1,
            MockUsageRecord(
                component="OpenAIEmbeddingClient",
                status="disabled",
                devOnly=False,
                developerMessage="Real OpenAI embeddings are configured for this runtime.",
            ),
        )
        embedding_records.insert(
            2,
            MockUsageRecord(
                component="MockEmbeddingClient",
                status="disabled",
                devOnly=True,
                developerMessage="Mock embeddings are bypassed because EMBEDDING_RUNTIME=openai.",
            ),
        )
    elif embedding_runtime == "ollama":
        embedding_records.insert(
            1,
            MockUsageRecord(
                component="OllamaEmbeddingClient",
                status="disabled",
                devOnly=False,
                developerMessage=(
                    f"Real Ollama embeddings are configured ({settings.embedding_model} @ {settings.ollama_base_url})."
                ),
            ),
        )
        embedding_records.insert(
            2,
            MockUsageRecord(
                component="MockEmbeddingClient",
                status="disabled",
                devOnly=True,
                developerMessage="Mock embeddings are bypassed because EMBEDDING_RUNTIME=ollama.",
            ),
        )
    else:
        embedding_records.insert(
            1,
            MockUsageRecord(
                component="MockEmbeddingClient",
                status="enabled",
                devOnly=True,
                developerMessage="Embedding values are deterministic mock vectors for schema and workflow validation.",
            ),
        )
    return embedding_records


def _chroma_fallback_events(job_id: str, chroma_result: ChromaWriteResult | None) -> list[FallbackEvent]:
    if chroma_result is None or chroma_result.status == "success":
        return []

    is_skipped = chroma_result.status == "skipped"
    return [
        FallbackEvent(
            id=new_id("fallback"),
            jobId=job_id,
            stepId="write_vectors",
            fallbackType="chroma_upsert_skipped" if is_skipped else "chroma_upsert_failed",
            originalError=chroma_result.message or "Chroma write did not complete",
            fallbackAction="Persisted embedding metadata without remote vector upsert",
            severity="info" if is_skipped else "warning",
            userVisible=False,
            developerMessage=chroma_result.message or "Chroma write did not complete",
            createdAt=utc_now(),
        )
    ]


def _boundary_warnings(logs, chroma_result: ChromaWriteResult | None) -> list[BoundaryWarning]:
    step_ids = {log.step_id for log in logs}
    history_status = "dev_only" if "retrieve_personal_history" in step_ids else "planned"
    history_message = (
        "V3-A personalized history retrieval is enabled for this workflow run."
        if history_status == "dev_only"
        else "Planned for V3 after V2 profile and feedback loops are stable."
    )
    knowledge_status = "dev_only" if "retrieve_aesthetic_knowledge" in step_ids else "planned"
    knowledge_message = (
        "V3-B aesthetic knowledge RAG is enabled for this workflow run."
        if knowledge_status == "dev_only"
        else "Planned for V3-B; external knowledge must remain explanation support only."
    )
    chroma_status, chroma_message = _chroma_boundary_status(chroma_result)
    return [
        BoundaryWarning(
            capability="Real vision / LLM runtime",
            status="not_used",
            developerMessage="Current workflow uses mock or heuristic local components, not real model calls.",
        ),
        BoundaryWarning(
            capability="ChromaDB runtime writes",
            status=chroma_status,
            developerMessage=chroma_message,
        ),
        BoundaryWarning(
            capability="Personalized history retrieval",
            status=history_status,
            developerMessage=history_message,
        ),
        BoundaryWarning(
            capability="Aesthetic knowledge RAG",
            status=knowledge_status,
            developerMessage=knowledge_message,
        ),
        BoundaryWarning(
            capability="Agent / MCP runtime",
            status="dev_only",
            developerMessage=(
                "V4-D Agent observation and optional stdio MCP catalog are implemented separately "
                "from the core analysis workflow; this job trace only covers aesthetic_analysis_v1."
            ),
        ),
        BoundaryWarning(
            capability="LangSmith / OpenTelemetry",
            status="not_used",
            developerMessage="Production observability pipelines are not connected in V4-E baseline.",
        ),
    ]


def _chroma_boundary_status(chroma_result: ChromaWriteResult | None) -> tuple[str, str]:
    if not settings.chroma_enabled:
        return (
            "not_used",
            "CHROMA_ENABLED=false; embedding metadata is saved locally without remote vector upsert.",
        )
    if chroma_result is None:
        return (
            "planned",
            "ChromaDB is enabled but no write result was recorded for this job.",
        )
    if chroma_result.status == "success":
        collection = chroma_result.collection_name or "inputs"
        return (
            "dev_only",
            f"V4-A wrote {chroma_result.upserted_count} input vectors to Chroma collection {collection}.",
        )
    if chroma_result.status == "skipped":
        return ("not_used", chroma_result.message or "Chroma write was skipped for this job.")
    return ("not_used", chroma_result.message or "Chroma write failed; embedding metadata was still saved.")

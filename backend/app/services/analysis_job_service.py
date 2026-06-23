from app.core.auth import CurrentUser
from app.core.config import settings
from app.schemas.analysis_job import AnalysisJobResponse, CreateAnalysisJobRequest
from app.schemas.analysis_debug import (
    AnalysisJobDebugResponse,
    BoundaryWarning,
    FallbackEvent,
    MockUsageRecord,
)
from app.schemas.common import new_id, utc_now
from app.schemas.report import ReportResponse
from app.services.failure_replay import build_failure_replay
from app.services.grouping_stability import build_grouping_stability_trace
from app.services.observability_trace import build_debug_traces
from app.services.schema_validation_summary import build_schema_validation_records
from app.vector_store.input_vector_store import ChromaWriteResult
from app.workflows.aesthetic_analysis_v1 import run_mock_aesthetic_analysis


class InputAccessDeniedError(ValueError):
    pass


class AnalysisJobService:
    def __init__(self, job_repository, input_repository, workflow_persistence) -> None:
        self.job_repository = job_repository
        self.input_repository = input_repository
        self.workflow_persistence = workflow_persistence

    def create_job(self, request: CreateAnalysisJobRequest, user_id: str) -> AnalysisJobResponse:
        now = utc_now()
        job = AnalysisJobResponse(
            id=new_id("job"),
            userId=user_id,
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
        for input_record in inputs:
            if input_record.user_id != user_id:
                raise InputAccessDeniedError("One or more inputs are not accessible for the current user")
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
        report = None
        if job.report_id is not None:
            report = self.workflow_persistence.report_repository.get(job.report_id)
        fallback_events = _chroma_fallback_events(job.id, chroma_result) + _knowledge_fallback_events(job.id, report)
        return build_failure_replay(job.id, job.status, logs, fallback_events)

    def get_job(self, job_id: str) -> AnalysisJobResponse | None:
        return self.job_repository.get(job_id)

    def get_debug(self, job_id: str, current_user: CurrentUser | None = None) -> AnalysisJobDebugResponse | None:
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
        fallback_events = _chroma_fallback_events(job.id, chroma_result) + _knowledge_fallback_events(job.id, report)
        grouping_inputs = []
        if report is not None:
            input_ids = [feature.input_id for feature in report.low_level_features]
            grouping_inputs = self.input_repository.get_many(input_ids)
        grouping_stability_trace = build_grouping_stability_trace(report, grouping_inputs)
        failure_replay = build_failure_replay(job.id, job.status, logs, fallback_events)
        auth_context = None
        if current_user is not None:
            from app.schemas.analysis_debug import AuthContextTrace

            auth_context = AuthContextTrace(
                authMode=current_user.auth_mode,
                resolvedUserId=current_user.user_id,
                sessionPresent=current_user.session_present,
            )
        return AnalysisJobDebugResponse(
            jobId=job.id,
            status=job.status,
            workflowTrace=logs,
            fallbackEvents=fallback_events,
            mockUsage=_mock_usage(),
            schemaValidation=schema_validation,
            boundaryWarnings=_boundary_warnings(logs, chroma_result, report),
            retrievalTrace=retrieval_trace,
            retrievalItems=retrieval_items,
            contextAssemblyTrace=context_assembly_trace,
            evaluationTrace=evaluation_trace,
            groupingStabilityTrace=grouping_stability_trace,
            failureReplay=failure_replay,
            authContext=auth_context,
        )


def _mock_usage() -> list[MockUsageRecord]:
    embedding_runtime = settings.embedding_runtime
    report_llm_runtime = settings.report_llm_runtime
    interpretation_records: list[MockUsageRecord]
    if report_llm_runtime == "ollama":
        interpretation_records = [
            MockUsageRecord(
                component="OllamaInterpretationGenerator",
                status="disabled",
                devOnly=False,
                developerMessage=(
                    f"Real Ollama report LLM is configured ({settings.report_llm_model} @ {settings.ollama_base_url})."
                ),
            ),
            MockUsageRecord(
                component="MockInterpretationGenerator",
                status="disabled",
                devOnly=True,
                developerMessage="Mock interpretations are bypassed because REPORT_LLM_RUNTIME=ollama.",
            ),
        ]
    elif report_llm_runtime == "openai":
        interpretation_records = [
            MockUsageRecord(
                component="MockInterpretationGenerator",
                status="enabled",
                devOnly=True,
                developerMessage="REPORT_LLM_RUNTIME=openai is reserved; V5-B ships ollama + mock paths.",
            ),
        ]
    else:
        interpretation_records = [
            MockUsageRecord(
                component="MockInterpretationGenerator",
                status="enabled",
                devOnly=True,
                developerMessage="Interpretations are generated by the local mock workflow and must not be treated as validated LLM output.",
            ),
        ]

    image_feature_records = _image_feature_mock_usage()
    music_feature_records = _music_feature_mock_usage()
    video_feature_records = _video_feature_mock_usage()
    embedding_records = [
        MockUsageRecord(
            component="MockFeatureExtractor",
            status="enabled",
            devOnly=True,
            developerMessage="Text feature extraction still uses mock or heuristic logic.",
        ),
        *image_feature_records,
        *music_feature_records,
        *video_feature_records,
        *interpretation_records,
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


def _knowledge_fallback_events(job_id: str, report: ReportResponse | None) -> list[FallbackEvent]:
    meta = None
    if report is not None and report.knowledge_context is not None:
        meta = report.knowledge_context.retrieval_meta
    if meta is None or meta.vector_path != "failed":
        return []

    error = meta.vector_error_message or "Knowledge vector retrieval failed"
    return [
        FallbackEvent(
            id=new_id("fallback"),
            jobId=job_id,
            stepId="retrieve_aesthetic_knowledge",
            fallbackType="knowledge_vector_retrieval_failed",
            originalError=error,
            fallbackAction="Used tag and knowledge-graph matches without vector reranking",
            severity="warning",
            userVisible=False,
            developerMessage=(
                "Knowledge vector retrieval degraded gracefully; report generation continued with "
                "static tag matches and graph context."
            ),
            createdAt=utc_now(),
        )
    ]


def _boundary_warnings(
    logs,
    chroma_result: ChromaWriteResult | None,
    report: ReportResponse | None = None,
) -> list[BoundaryWarning]:
    step_ids = {log.step_id for log in logs}
    history_status = "dev_only" if "retrieve_personal_history" in step_ids else "planned"
    history_message = (
        "V3-A personalized history retrieval is enabled for this workflow run."
        if history_status == "dev_only"
        else "Planned for V3 after V2 profile and feedback loops are stable."
    )
    knowledge_status = "dev_only" if "retrieve_aesthetic_knowledge" in step_ids else "planned"
    knowledge_message = _knowledge_boundary_message(knowledge_status, report)
    chroma_status, chroma_message = _chroma_boundary_status(chroma_result)
    llm_status, llm_message = _runtime_boundary_status()
    return [
        BoundaryWarning(
            capability="Real vision / LLM runtime",
            status=llm_status,
            developerMessage=llm_message,
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


def _knowledge_boundary_message(knowledge_status: str, report: ReportResponse | None) -> str:
    meta = None
    if report is not None and report.knowledge_context is not None:
        meta = report.knowledge_context.retrieval_meta
    if meta is not None and meta.vector_path == "failed":
        return (
            "V3-B aesthetic knowledge RAG degraded for this workflow run: vector rerank failed, "
            "so static tag matches and graph context were used."
        )
    if knowledge_status == "dev_only":
        return "V3-B aesthetic knowledge RAG is enabled for this workflow run."
    return "Planned for V3-B; external knowledge must remain explanation support only."


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


def _report_llm_boundary_status() -> tuple[str, str]:
    runtime = settings.report_llm_runtime
    if runtime == "ollama":
        return (
            "dev_only",
            f"V5-B Ollama report LLM enabled ({settings.report_llm_model}); feature extraction remains mock/heuristic.",
        )
    if runtime == "openai":
        return (
            "planned",
            "REPORT_LLM_RUNTIME=openai is reserved; V5-B ships ollama + mock paths.",
        )
    return (
        "not_used",
        "REPORT_LLM_RUNTIME=mock; interpretations and insights use MockInterpretationGenerator.",
    )


def _image_feature_mock_usage() -> list[MockUsageRecord]:
    runtime = settings.image_feature_runtime
    if runtime == "ollama_vision":
        return [
            MockUsageRecord(
                component="OllamaVisionImageFeatureExtractor",
                status="disabled",
                devOnly=False,
                developerMessage=(
                    f"Real image feature runtime is configured ({settings.image_feature_model} @ {settings.ollama_base_url})."
                ),
            ),
            MockUsageRecord(
                component="MockImageFeatureExtractor",
                status="disabled",
                devOnly=True,
                developerMessage="Mock image features are bypassed because IMAGE_FEATURE_RUNTIME=ollama_vision.",
            ),
        ]
    if runtime == "disabled":
        return [
            MockUsageRecord(
                component="MockImageFeatureExtractor",
                status="disabled",
                devOnly=True,
                developerMessage="IMAGE_FEATURE_RUNTIME=disabled; image inputs fail fast instead of using mock vision.",
            )
        ]
    return [
        MockUsageRecord(
            component="MockImageFeatureExtractor",
            status="enabled",
            devOnly=True,
            developerMessage=(
                "V6-A image understanding uses a dev-only mock placeholder; it must not be treated as real vision."
            ),
        )
    ]


def _music_feature_mock_usage() -> list[MockUsageRecord]:
    runtime = settings.music_feature_runtime
    if runtime == "disabled":
        return [
            MockUsageRecord(
                component="MockAudioMusicFeatureExtractor",
                status="disabled",
                devOnly=True,
                developerMessage="MUSIC_FEATURE_RUNTIME=disabled; music inputs fail fast instead of using mock music.",
            )
        ]
    if runtime == "mock":
        return [
            MockUsageRecord(
                component="MockAudioMusicFeatureExtractor",
                status="enabled",
                devOnly=True,
                developerMessage=(
                    "V6-B music understanding uses a dev-only mock placeholder; it must not be treated as real audio."
                ),
            )
        ]
    if runtime == "text_notes":
        return [
            MockUsageRecord(
                component="TextNotesAudioMusicFeatureExtractor",
                status="disabled",
                devOnly=False,
                developerMessage="Music features are derived from user-provided lyrics, transcript, or notes.",
            ),
            MockUsageRecord(
                component="MockAudioMusicFeatureExtractor",
                status="disabled",
                devOnly=True,
                developerMessage="Mock music features are bypassed because MUSIC_FEATURE_RUNTIME=text_notes.",
            ),
        ]
    return [
        MockUsageRecord(
            component="MetadataOnlyAudioMusicFeatureExtractor",
            status="disabled",
            devOnly=False,
            developerMessage="Music features use metadata only; no audio content is parsed.",
        ),
        MockUsageRecord(
            component="MockAudioMusicFeatureExtractor",
            status="disabled",
            devOnly=True,
            developerMessage="Mock music features are bypassed because MUSIC_FEATURE_RUNTIME=metadata_only.",
        ),
    ]


def _video_feature_mock_usage() -> list[MockUsageRecord]:
    runtime = settings.video_feature_runtime
    if runtime == "disabled":
        return [
            MockUsageRecord(
                component="MockVideoFeatureExtractor",
                status="disabled",
                devOnly=True,
                developerMessage="VIDEO_FEATURE_RUNTIME=disabled; video inputs fail fast instead of using mock video.",
            )
        ]
    if runtime == "mock":
        return [
            MockUsageRecord(
                component="MockVideoFeatureExtractor",
                status="enabled",
                devOnly=True,
                developerMessage=(
                    "V6-C video understanding uses a dev-only mock placeholder; it must not be treated as real video."
                ),
            )
        ]
    if runtime == "text_notes":
        return [
            MockUsageRecord(
                component="TextNotesVideoFeatureExtractor",
                status="disabled",
                devOnly=False,
                developerMessage="Video features are derived from user-provided subtitles, description, or shot notes.",
            ),
            MockUsageRecord(
                component="MockVideoFeatureExtractor",
                status="disabled",
                devOnly=True,
                developerMessage="Mock video features are bypassed because VIDEO_FEATURE_RUNTIME=text_notes.",
            ),
        ]
    return [
        MockUsageRecord(
            component="MetadataOnlyVideoFeatureExtractor",
            status="disabled",
            devOnly=False,
            developerMessage="Video features use metadata only; no frames or subtitles are parsed.",
        ),
        MockUsageRecord(
            component="MockVideoFeatureExtractor",
            status="disabled",
            devOnly=True,
            developerMessage="Mock video features are bypassed because VIDEO_FEATURE_RUNTIME=metadata_only.",
        ),
    ]


def _runtime_boundary_status() -> tuple[str, str]:
    report_status, report_message = _report_llm_boundary_status()
    image_runtime = settings.image_feature_runtime
    music_runtime = settings.music_feature_runtime
    video_runtime = settings.video_feature_runtime
    if image_runtime == "ollama_vision":
        image_message = f"IMAGE_FEATURE_RUNTIME=ollama_vision configured ({settings.image_feature_model})."
        status = "dev_only" if report_status == "dev_only" else report_status
    elif image_runtime == "disabled":
        image_message = "IMAGE_FEATURE_RUNTIME=disabled; image content parsing fails fast."
        status = report_status
    else:
        image_message = "IMAGE_FEATURE_RUNTIME=mock; image features are dev-only placeholders."
        status = report_status if report_status == "dev_only" else "not_used"

    if music_runtime == "disabled":
        music_message = "MUSIC_FEATURE_RUNTIME=disabled; music content parsing fails fast."
    elif music_runtime == "mock":
        music_message = "MUSIC_FEATURE_RUNTIME=mock; music features are dev-only placeholders."
        status = "dev_only" if status == "not_used" else status
    elif music_runtime == "text_notes":
        music_message = "MUSIC_FEATURE_RUNTIME=text_notes; music features use user-provided lyrics/transcript/notes."
    else:
        music_message = "MUSIC_FEATURE_RUNTIME=metadata_only; music inputs do not claim parsed audio."

    if video_runtime == "disabled":
        video_message = "VIDEO_FEATURE_RUNTIME=disabled; video content parsing fails fast."
    elif video_runtime == "mock":
        video_message = "VIDEO_FEATURE_RUNTIME=mock; video features are dev-only placeholders."
        status = "dev_only" if status == "not_used" else status
    elif video_runtime == "text_notes":
        video_message = "VIDEO_FEATURE_RUNTIME=text_notes; video features use user-provided subtitles/descriptions/shot notes."
    else:
        video_message = "VIDEO_FEATURE_RUNTIME=metadata_only; video inputs do not claim parsed frames or subtitles."
    return (status, f"{report_message} {image_message} {music_message} {video_message}")

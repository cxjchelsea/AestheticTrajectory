from app.repositories.analysis_log_repository import AnalysisLogRepository
from app.repositories.embedding_record_repository import EmbeddingRecordRepository
from app.repositories.feature_repository import FeatureRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.memory_store import MemoryStore
from app.repositories.report_repository import ReportRepository
from app.repositories.knowledge_graph_repository import KnowledgeGraphRepository
from app.repositories.timeline_repository import TimelineRepository
from app.repositories.chroma_debug_store import chroma_write_results
from app.repositories.workflow_persistence import WorkflowPersistence
from app.ai.factory import get_interpretation_generator
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import new_id, utc_now
from app.schemas.input import AestheticInputResponse
from app.schemas.report import ReportResponse
from app.workflows.steps.analysis_logging import record_step
from app.workflows.steps.build_embedding_text import build_embedding_text
from app.workflows.steps.cluster_inputs import cluster_inputs
from app.workflows.steps.extract_features import extract_features
from app.workflows.steps.generate_embeddings import generate_embeddings
from app.workflows.steps.compute_report_evaluation import compute_report_evaluation
from app.workflows.steps.generate_interpretations import generate_interpretations
from app.workflows.steps.generate_report import generate_report
from app.workflows.steps.retrieve_aesthetic_knowledge import retrieve_aesthetic_knowledge
from app.workflows.steps.retrieve_personal_history import retrieve_personal_history
from app.workflows.steps.update_trajectory import update_trajectory
from app.workflows.steps.write_vectors import write_vectors


def run_mock_aesthetic_analysis(
    job: AnalysisJobResponse,
    inputs: list[AestheticInputResponse],
    persistence: WorkflowPersistence,
) -> AnalysisJobResponse:
    feature_result = record_step(
        persistence.analysis_log_repository,
        job.id,
        "extract_features",
        lambda: extract_features(inputs),
    )
    persistence.feature_repository.save_many(feature_result)

    embeddings = record_step(
        persistence.analysis_log_repository,
        job.id,
        "generate_embeddings",
        lambda: generate_embeddings(inputs, feature_result),
    )
    feature_by_input_id = {feature.input_id: feature for feature in feature_result}
    embedding_texts = {
        input_record.id: build_embedding_text(
            input_record,
            feature_by_input_id.get(input_record.id),
        )
        for input_record in inputs
    }

    def persist_vectors():
        records, chroma_result = write_vectors(
            job,
            inputs,
            embeddings,
            embedding_texts=embedding_texts,
        )
        if chroma_result.status in {"skipped", "failed", "success"}:
            persistence.save_chroma_write_result(job.id, chroma_result)
        return records

    embedding_records = record_step(
        persistence.analysis_log_repository,
        job.id,
        "write_vectors",
        persist_vectors,
    )
    persistence.embedding_record_repository.save_many(embedding_records)

    groups = record_step(
        persistence.analysis_log_repository,
        job.id,
        "cluster_inputs",
        lambda: cluster_inputs(
            [input_record.id for input_record in inputs],
            feature_result,
            embeddings,
        ),
    )
    report_id = new_id("report")
    history_context = record_step(
        persistence.analysis_log_repository,
        job.id,
        "retrieve_personal_history",
        lambda: retrieve_personal_history(
            job.user_id,
            report_id,
            feature_result,
            persistence.report_repository,
            persistence.feedback_repository,
        ),
    )
    knowledge_context = record_step(
        persistence.analysis_log_repository,
        job.id,
        "retrieve_aesthetic_knowledge",
        lambda: retrieve_aesthetic_knowledge(
            feature_result,
            graph_repository=persistence.knowledge_graph_repository,
        ),
    )
    interpretation_generator = get_interpretation_generator()
    interpretations, insights = record_step(
        persistence.analysis_log_repository,
        job.id,
        "generate_interpretations",
        lambda: generate_interpretations(
            groups,
            feature_result,
            [input_record.id for input_record in inputs],
            history_context,
            knowledge_context,
            interpretation_generator,
        ),
        model_name=interpretation_generator.model_name,
        prompt_version=interpretation_generator.prompt_version,
    )
    report = record_step(
        persistence.analysis_log_repository,
        job.id,
        "generate_report",
        lambda: generate_report(
            report_id,
            feature_result,
            groups,
            interpretations,
            insights,
            history_context,
            knowledge_context,
        ),
    )
    evaluation = record_step(
        persistence.analysis_log_repository,
        job.id,
        "compute_report_evaluation",
        lambda: compute_report_evaluation(
            report,
            job.id,
            persistence.analysis_log_repository,
        ),
    )
    report = report.model_copy(update={"evaluation_metrics": evaluation.metrics})
    record_step(
        persistence.analysis_log_repository,
        job.id,
        "save_report",
        lambda: persistence.report_repository.save(report, user_id=job.user_id, job_id=job.id),
    )

    if persistence.timeline_repository is not None:
        record_step(
            persistence.analysis_log_repository,
            job.id,
            "update_trajectory",
            lambda: update_trajectory(
                job.user_id,
                report,
                persistence.report_repository,
                persistence.timeline_repository,
            ),
        )

    return AnalysisJobResponse(
        id=job.id,
        userId=job.user_id,
        status="completed",
        inputCount=job.input_count,
        errorMessage=None,
        reportId=report.report_id,
        createdAt=job.created_at,
        startedAt=job.started_at,
        finishedAt=utc_now(),
    )


def memory_workflow_persistence(store: MemoryStore) -> WorkflowPersistence:
    return WorkflowPersistence(
        feature_repository=FeatureRepository(store),
        embedding_record_repository=EmbeddingRecordRepository(store),
        report_repository=ReportRepository(store),
        analysis_log_repository=AnalysisLogRepository(store),
        feedback_repository=FeedbackRepository(store),
        timeline_repository=TimelineRepository(store),
        knowledge_graph_repository=KnowledgeGraphRepository(),
        chroma_write_results=chroma_write_results,
    )

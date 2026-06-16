from app.repositories.memory_store import MemoryStore
from app.repositories.report_repository import ReportRepository
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import new_id, utc_now
from app.schemas.input import AestheticInputResponse
from app.schemas.report import ReportResponse
from app.workflows.steps.cluster_inputs import cluster_inputs
from app.workflows.steps.extract_features import extract_features
from app.workflows.steps.generate_embeddings import generate_embeddings
from app.workflows.steps.generate_report import generate_report
from app.workflows.steps.write_vectors import write_vectors


def run_mock_aesthetic_analysis(
    store: MemoryStore,
    job: AnalysisJobResponse,
    inputs: list[AestheticInputResponse],
) -> AnalysisJobResponse:
    feature_result = extract_features(inputs)
    for feature in feature_result:
        store.features[feature.input_id] = feature

    embeddings = generate_embeddings(inputs, feature_result)
    embedding_records = write_vectors(job, inputs, embeddings)
    for record in embedding_records:
        store.embedding_records[record.id] = record

    groups, interpretations, insights = cluster_inputs(
        [input_record.id for input_record in inputs],
        feature_result,
        embeddings,
    )
    report = generate_report(new_id("report"), feature_result, groups, interpretations, insights)
    ReportRepository(store).save(report)

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

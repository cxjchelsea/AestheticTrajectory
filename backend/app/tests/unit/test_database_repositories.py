from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import persistence  # noqa: F401
from app.repositories.database_repositories import (
    DatabaseAnalysisJobRepository,
    DatabaseAnalysisLogRepository,
    DatabaseEmbeddingRecordRepository,
    DatabaseFeatureRepository,
    DatabaseFeedbackRepository,
    DatabaseInputRepository,
    DatabaseReportRepository,
)
from app.repositories.workflow_persistence import WorkflowPersistence
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import utc_now
from app.schemas.feedback import CreateInsightFeedbackRequest
from app.schemas.input import AestheticInputResponse
from app.services.feedback_service import FeedbackService
from app.workflows.aesthetic_analysis_v1 import run_mock_aesthetic_analysis


def test_database_repositories_persist_workflow_outputs_across_sessions() -> None:
    session_factory = _session_factory()
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id=f"input_{index}",
            userId="user_anonymous",
            type="text",
            contentText=f"sample {index}",
            fileUrl=None,
            source="test",
            title=f"sample {index}",
            description=None,
            createdAt=now,
        )
        for index in range(3)
    ]
    job = AnalysisJobResponse(
        id="job_001",
        userId="user_anonymous",
        status="created",
        inputCount=3,
        errorMessage=None,
        reportId=None,
        createdAt=now,
        startedAt=now,
        finishedAt=None,
    )

    with session_factory() as session:
        input_repository = DatabaseInputRepository(session)
        for input_record in inputs:
            input_repository.save(input_record)
        DatabaseAnalysisJobRepository(session).save(job)
        result = run_mock_aesthetic_analysis(
            job,
            inputs,
            WorkflowPersistence(
                feature_repository=DatabaseFeatureRepository(session),
                embedding_record_repository=DatabaseEmbeddingRecordRepository(session),
                report_repository=DatabaseReportRepository(session),
                analysis_log_repository=DatabaseAnalysisLogRepository(session),
            ),
        )
        DatabaseAnalysisJobRepository(session).save(result)
        session.commit()

    with session_factory() as session:
        saved_job = DatabaseAnalysisJobRepository(session).get("job_001")
        assert saved_job is not None
        assert saved_job.status == "completed"
        assert saved_job.report_id is not None

        report = DatabaseReportRepository(session).get(saved_job.report_id)
        assert report is not None
        assert report.insights
        assert report.insights[0].evidence_refs

        logs = DatabaseAnalysisLogRepository(session).get_for_job("job_001")
        assert {log.step_id for log in logs} >= {
            "extract_features",
            "generate_embeddings",
            "write_vectors",
            "cluster_inputs",
            "generate_report",
            "save_report",
        }
        assert all(log.status == "success" for log in logs)

        feedback = FeedbackService(DatabaseFeedbackRepository(session)).create_feedback(
            report.insights[0].insight_id,
            CreateInsightFeedbackRequest(rating="somewhat_me", comment="sqlite validation"),
        )
        session.commit()
        assert feedback.insight_id == report.insights[0].insight_id


def _session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

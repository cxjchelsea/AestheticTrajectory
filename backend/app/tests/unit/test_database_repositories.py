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
    DatabaseProfileRepository,
    DatabaseReportRepository,
)
from app.repositories.workflow_persistence import WorkflowPersistence
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import utc_now
from app.schemas.feedback import CreateInsightFeedbackRequest
from app.schemas.feedback import InsightFeedbackResponse
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
                feedback_repository=DatabaseFeedbackRepository(session),
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
            "retrieve_personal_history",
            "retrieve_aesthetic_knowledge",
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


def test_database_report_repository_lists_reports_by_user() -> None:
    session_factory = _session_factory()

    first_report_id = _persist_report(session_factory, "user_a", "job_user_a_1", "a1")
    second_report_id = _persist_report(session_factory, "user_a", "job_user_a_2", "a2")
    _persist_report(session_factory, "user_b", "job_user_b_1", "b1")

    with session_factory() as session:
        history = DatabaseReportRepository(session).list_by_user("user_a", limit=20, offset=0)

    assert history.total == 2
    assert [report.report_id for report in history.reports] == [second_report_id, first_report_id]
    assert all(report.input_count == 3 for report in history.reports)


def test_database_report_repository_lists_recent_reports_by_user() -> None:
    session_factory = _session_factory()

    first_report_id = _persist_report(session_factory, "user_recent", "job_recent_1", "recent1")
    second_report_id = _persist_report(session_factory, "user_recent", "job_recent_2", "recent2")
    _persist_report(session_factory, "user_other", "job_recent_other", "recent_other")

    with session_factory() as session:
        recent = DatabaseReportRepository(session).list_recent_by_user("user_recent", limit=2)

    assert [report.report_id for report in recent] == [second_report_id, first_report_id]


def test_database_profile_repository_builds_evidence_backed_profile() -> None:
    session_factory = _session_factory()
    report_id = _persist_report(session_factory, "user_profile", "job_profile", "profile")

    with session_factory() as session:
        report = DatabaseReportRepository(session).get(report_id)
        assert report is not None
        feedback = InsightFeedbackResponse(
            id="feedback_negative",
            userId="user_profile",
            insightId=report.insights[0].insight_id,
            interpretationId=None,
            rating="not_me",
            comment="不符合我",
            createdAt=utc_now(),
        )
        DatabaseFeedbackRepository(session).save(feedback)
        profile = DatabaseProfileRepository(session).get_or_build("user_profile")
        session.commit()

    assert profile.profile is not None
    assert profile.profile.items
    assert all(item.evidence for item in profile.profile.items)
    rejected_items = [item for item in profile.profile.items if item.status == "rejected"]
    assert rejected_items
    assert rejected_items[0].weight < 0
    assert rejected_items[0].evidence[0].direction == "negative"


def test_database_feedback_repository_updates_existing_target_feedback() -> None:
    session_factory = _session_factory()
    report_id = _persist_report(session_factory, "user_anonymous", "job_feedback_update", "feedback_update")

    with session_factory() as session:
        report = DatabaseReportRepository(session).get(report_id)
        assert report is not None
        service = FeedbackService(DatabaseFeedbackRepository(session))

        first_feedback = service.create_feedback(
            report.insights[0].insight_id,
            CreateInsightFeedbackRequest(rating="somewhat_me", comment="first"),
        )
        second_feedback = service.create_feedback(
            report.insights[0].insight_id,
            CreateInsightFeedbackRequest(rating="not_me", comment="updated"),
        )
        current_feedback = service.get_feedback(report.insights[0].insight_id)
        profile = DatabaseProfileRepository(session).get_or_build("user_anonymous")
        session.commit()

    assert second_feedback.id == first_feedback.id
    assert current_feedback is not None
    assert current_feedback.rating == "not_me"
    assert profile.profile is not None
    feedback_evidence = [
        evidence
        for item in profile.profile.items
        for evidence in item.evidence
        if evidence.evidence_type == "feedback"
    ]
    assert len(feedback_evidence) == 1
    assert feedback_evidence[0].direction == "negative"


def _session_factory():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _persist_report(session_factory, user_id: str, job_id: str, input_prefix: str) -> str:
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id=f"{input_prefix}_input_{index}",
            userId=user_id,
            type="text",
            contentText=f"{input_prefix} sample {index}",
            fileUrl=None,
            source="test",
            title=f"{input_prefix} sample {index}",
            description=None,
            createdAt=now,
        )
        for index in range(3)
    ]
    job = AnalysisJobResponse(
        id=job_id,
        userId=user_id,
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
                feedback_repository=DatabaseFeedbackRepository(session),
            ),
        )
        DatabaseAnalysisJobRepository(session).save(result)
        session.commit()

    assert result.report_id is not None
    return result.report_id

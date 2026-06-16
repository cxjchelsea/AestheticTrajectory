from app.repositories.memory_store import MemoryStore
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.common import utc_now
from app.schemas.input import AestheticInputResponse
from app.workflows.aesthetic_analysis_v1 import run_mock_aesthetic_analysis


def test_mock_workflow_completes_and_saves_report() -> None:
    store = MemoryStore()
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

    result = run_mock_aesthetic_analysis(store, job, inputs)

    assert result.status == "completed"
    assert result.report_id is not None
    assert result.report_id in store.reports
    assert store.embedding_records
    report = store.reports[result.report_id]
    assert report.similarity_groups
    assert report.similarity_groups[0].common_features
    assert "不代表长期偏好或绝对分类" in report.similarity_groups[0].uncertainty

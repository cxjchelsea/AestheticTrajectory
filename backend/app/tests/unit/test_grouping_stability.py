from app.repositories.memory_store import MemoryStore
from app.schemas.common import utc_now
from app.schemas.input import AestheticInputResponse
from app.schemas.interpretation import SimilarityGroup
from app.services.failure_replay import build_failure_replay
from app.services.grouping_stability import build_grouping_stability
from app.schemas.analysis_debug import FallbackEvent
from app.schemas.analysis_log import AnalysisLogRecord
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence, run_mock_aesthetic_analysis
from app.repositories.analysis_job_repository import AnalysisJobRepository
from app.schemas.analysis_job import AnalysisJobResponse


def _run_workflow(store: MemoryStore) -> tuple[str, list[AestheticInputResponse]]:
    now = utc_now()
    inputs = [
        AestheticInputResponse(
            id=f"input_gs_{index}",
            userId="user_anonymous",
            type="text",
            contentText=f"quiet room sample {index}",
            fileUrl=None,
            source="test",
            title=f"Quiet room {index}",
            description="low density",
            createdAt=now,
        )
        for index in range(3)
    ]
    for item in inputs:
        store.inputs[item.id] = item
    job = AnalysisJobResponse(
        id="job_grouping_stability",
        userId="user_anonymous",
        status="created",
        inputCount=3,
        errorMessage=None,
        reportId=None,
        createdAt=now,
        startedAt=now,
        finishedAt=None,
    )
    result = run_mock_aesthetic_analysis(job, inputs, memory_workflow_persistence(store))
    return result.report_id, inputs


def test_grouping_stability_matches_recomputed_clusters() -> None:
    store = MemoryStore()
    report_id, inputs = _run_workflow(store)
    report = store.reports[report_id]

    result = build_grouping_stability(report, inputs)

    assert result.score == 1.0
    assert result.pair_count == 3
    assert result.consistent_pair_count == 3
    assert result.recomputed_group_count == len(report.similarity_groups)
    assert "长期偏好" in result.disclaimer


def test_grouping_stability_detects_persisted_drift() -> None:
    store = MemoryStore()
    report_id, inputs = _run_workflow(store)
    report = store.reports[report_id]
    drifted = report.model_copy(
        update={
            "similarity_groups": [
                SimilarityGroup(
                    groupId="group_drift",
                    name="drift",
                    inputIds=[inputs[0].id, inputs[1].id],
                    commonFeatures=["density:low"],
                    uncertainty="test drift",
                )
            ]
        }
    )

    result = build_grouping_stability(drifted, inputs)

    assert result.score is not None
    assert result.score < 1.0
    assert any(not detail.consistent for detail in result.pair_details)


def test_grouping_stability_null_when_sample_too_small() -> None:
    store = MemoryStore()
    report_id, inputs = _run_workflow(store)
    report = store.reports[report_id]
    small_report = report.model_copy(update={"low_level_features": report.low_level_features[:2]})

    result = build_grouping_stability(small_report, inputs[:2])

    assert result.score is None
    assert result.message
    assert result.pair_count == 0

import importlib

import pytest

from app.ai.interpretation_generator import InterpretationGenerator
from app.ai.mock.mock_interpretation_generator import MockInterpretationGenerator
from app.repositories.memory_store import MemoryStore
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.report import Insight
from app.workflows.aesthetic_analysis_v1 import memory_workflow_persistence, run_mock_aesthetic_analysis
from app.workflows.steps.generate_interpretations import generate_interpretations


class FixedInterpretationGenerator:
    @property
    def model_name(self) -> str:
        return "fixed-test-model"

    @property
    def prompt_version(self) -> str:
        return "interpretations.generate.v1"

    def generate(self, groups, features, input_ids, history_context=None, knowledge_context=None):
        return (
            [
                PossibleInterpretation(
                    id="interpretation_test",
                    name="测试解释",
                    confidence=0.8,
                    evidenceRefs=[input_ids[0]],
                    uncertainty="测试 uncertainty。",
                )
            ],
            [
                Insight(
                    insightId="insight_test",
                    title="测试洞察",
                    observation="测试观察。",
                    evidenceRefs=[input_ids[0]],
                    interpretation="测试解释句。",
                    uncertainty="测试 uncertainty。",
                    confidence=0.75,
                )
            ],
        )


def test_generate_interpretations_uses_injected_generator() -> None:
    groups = [
        SimilarityGroup(
            groupId="group_001",
            name="测试组",
            inputIds=["input_a", "input_b", "input_c"],
            commonFeatures=["density:low"],
            uncertainty="测试",
        )
    ]
    interpretations, insights = generate_interpretations(
        groups,
        [],
        ["input_a", "input_b", "input_c"],
        generator=FixedInterpretationGenerator(),
    )
    assert interpretations[0].name == "测试解释"
    assert insights[0].title == "测试洞察"


def test_v5b_workflow_records_generate_interpretations_step() -> None:
    store = MemoryStore()
    persistence = memory_workflow_persistence(store)
    inputs = _sample_inputs()
    job = _sample_job()
    result = run_mock_aesthetic_analysis(job, inputs, persistence)
    logs = store.analysis_logs
    step_ids = {log.step_id for log in logs.values()}
    assert result.status == "completed"
    assert "generate_interpretations" in step_ids


def test_v5b_mock_runtime_keeps_mock_interpretation_generator_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPORT_LLM_RUNTIME", "mock")
    import app.core.config as config_module

    importlib.reload(config_module)
    importlib.reload(importlib.import_module("app.services.analysis_job_service"))

    from app.services.analysis_job_service import _mock_usage

    components = {item.component: item for item in _mock_usage()}
    assert components["MockInterpretationGenerator"].status == "enabled"


def test_v5b_ollama_runtime_marks_real_llm_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPORT_LLM_RUNTIME", "ollama")
    import app.core.config as config_module

    importlib.reload(config_module)
    importlib.reload(importlib.import_module("app.services.analysis_job_service"))

    from app.services.analysis_job_service import _mock_usage, _report_llm_boundary_status

    status, message = _report_llm_boundary_status()
    assert status == "dev_only"
    assert "Ollama" in message

    components = {item.component: item for item in _mock_usage()}
    assert components["OllamaInterpretationGenerator"].status == "disabled"
    assert components["MockInterpretationGenerator"].status == "disabled"


def _sample_inputs():
    from app.schemas.common import utc_now
    from app.schemas.input import AestheticInputResponse

    now = utc_now()
    return [
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


def _sample_job():
    from app.schemas.analysis_job import AnalysisJobResponse
    from app.schemas.common import utc_now

    now = utc_now()
    return AnalysisJobResponse(
        id="job_v5b_test",
        userId="user_anonymous",
        status="created",
        inputCount=3,
        errorMessage=None,
        reportId=None,
        createdAt=now,
        startedAt=now,
        finishedAt=None,
    )

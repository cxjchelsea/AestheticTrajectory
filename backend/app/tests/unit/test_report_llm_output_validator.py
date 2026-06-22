import pytest

from app.ai.validators.report_llm_output_validator import validate_and_convert_report_llm_output
from app.schemas.report_llm_output import InsightLLMItem, InterpretationLLMItem, InterpretationLLMOutput


def _payload(**overrides: object) -> InterpretationLLMOutput:
    base = {
        "promptVersion": "interpretations.generate.v1",
        "modelName": "test-model",
        "interpretations": [
            InterpretationLLMItem(
                id="interpretation_001",
                name="低密度倾向",
                confidence=0.7,
                evidenceRefs=["input_a"],
                uncertainty="样本较少。",
            )
        ],
        "insights": [
            InsightLLMItem(
                insightId="insight_001",
                title="观察到低密度结构",
                observation="输入中重复出现低密度特征。",
                interpretation="这可能表示当前样本偏向留白构图。",
                evidenceRefs=["input_a"],
                uncertainty="不是人格诊断。",
                confidence=0.65,
            )
        ],
    }
    base.update(overrides)
    return InterpretationLLMOutput.model_validate(base)


def test_validate_report_llm_output_accepts_valid_payload() -> None:
    interpretations, insights = validate_and_convert_report_llm_output(
        _payload(),
        ["input_a"],
        "interpretations.generate.v1",
    )
    assert len(interpretations) == 1
    assert len(insights) == 1
    assert interpretations[0].evidence_refs == ["input_a"]


def test_validate_report_llm_output_rejects_foreign_evidence_refs() -> None:
    payload = _payload()
    payload.interpretations[0].evidence_refs.append("input_foreign")
    with pytest.raises(ValueError, match="evidenceRefs"):
        validate_and_convert_report_llm_output(payload, ["input_a"], "interpretations.generate.v1")


def test_validate_report_llm_output_rejects_governance_terms() -> None:
    payload = _payload()
    payload.insights[0].interpretation = "你的人格诊断结果就是孤独型。"
    with pytest.raises(ValueError, match="Governance violation"):
        validate_and_convert_report_llm_output(payload, ["input_a"], "interpretations.generate.v1")

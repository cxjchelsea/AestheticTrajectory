from app.schemas.interpretation import PossibleInterpretation
from app.schemas.report import Insight
from app.schemas.report_llm_output import InterpretationLLMOutput

GOVERNANCE_BANNED_PHRASES = (
    "人格诊断",
    "心理评估",
    "心理诊断",
    "命运",
    "灵魂",
    "星座",
    "你一定",
    "你就是",
    "消费规训",
)


def validate_and_convert_report_llm_output(
    payload: InterpretationLLMOutput,
    input_ids: list[str],
    expected_prompt_version: str,
) -> tuple[list[PossibleInterpretation], list[Insight]]:
    allowed_input_ids = set(input_ids)
    if payload.prompt_version != expected_prompt_version:
        raise ValueError(f"Unexpected promptVersion: {payload.prompt_version}")

    interpretations: list[PossibleInterpretation] = []
    for item in payload.interpretations:
        _assert_evidence_refs(item.evidence_refs, allowed_input_ids)
        _assert_governance_text(item.name, item.uncertainty)
        interpretations.append(
            PossibleInterpretation(
                id=item.id,
                name=item.name,
                confidence=item.confidence,
                evidenceRefs=item.evidence_refs,
                uncertainty=item.uncertainty,
            )
        )

    insights: list[Insight] = []
    for item in payload.insights:
        _assert_evidence_refs(item.evidence_refs, allowed_input_ids)
        combined_text = " ".join(
            [item.title, item.observation, item.interpretation, item.uncertainty]
        )
        _assert_governance_text(combined_text)
        insights.append(
            Insight(
                insightId=item.insight_id,
                title=item.title,
                observation=item.observation,
                evidenceRefs=item.evidence_refs,
                interpretation=item.interpretation,
                uncertainty=item.uncertainty,
                confidence=item.confidence,
            )
        )

    return interpretations, insights


def _assert_evidence_refs(evidence_refs: list[str], allowed_input_ids: set[str]) -> None:
    invalid_refs = [ref for ref in evidence_refs if ref not in allowed_input_ids]
    if invalid_refs:
        raise ValueError(f"evidenceRefs must reference current input ids only: {invalid_refs}")


def _assert_governance_text(*parts: str) -> None:
    combined = " ".join(part for part in parts if part)
    sanitized = combined
    for phrase in GOVERNANCE_BANNED_PHRASES:
        sanitized = sanitized.replace(f"不是{phrase}", "")
        sanitized = sanitized.replace(f"并非{phrase}", "")
    for phrase in GOVERNANCE_BANNED_PHRASES:
        if phrase in sanitized:
            raise ValueError(f"Governance violation: banned phrase '{phrase}' in LLM output")

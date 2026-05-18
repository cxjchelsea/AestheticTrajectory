from app.ai.mock.mock_interpretation_generator import MockInterpretationGenerator
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.report import Insight


def cluster_inputs(input_ids: list[str]) -> tuple[list[SimilarityGroup], list[PossibleInterpretation], list[Insight]]:
    generator = MockInterpretationGenerator()
    evidence_refs = input_ids[:3]
    return generator.group(input_ids), generator.interpret(evidence_refs), generator.insights(evidence_refs)

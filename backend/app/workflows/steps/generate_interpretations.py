from app.ai.factory import get_interpretation_generator
from app.ai.interpretation_generator import InterpretationGenerator
from app.schemas.feature import InputFeature
from app.schemas.history_context import PersonalHistoryContext
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.knowledge_context import AestheticKnowledgeContext
from app.schemas.report import Insight


def generate_interpretations(
    groups: list[SimilarityGroup],
    features: list[InputFeature],
    input_ids: list[str],
    history_context: PersonalHistoryContext | None = None,
    knowledge_context: AestheticKnowledgeContext | None = None,
    generator: InterpretationGenerator | None = None,
) -> tuple[list[PossibleInterpretation], list[Insight]]:
    active_generator = generator or get_interpretation_generator()
    return active_generator.generate(
        groups,
        features,
        input_ids,
        history_context=history_context,
        knowledge_context=knowledge_context,
    )

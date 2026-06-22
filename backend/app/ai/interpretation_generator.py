from typing import Protocol

from app.schemas.feature import InputFeature
from app.schemas.history_context import PersonalHistoryContext
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.knowledge_context import AestheticKnowledgeContext
from app.schemas.report import Insight


class InterpretationGenerator(Protocol):
    @property
    def model_name(self) -> str: ...

    @property
    def prompt_version(self) -> str: ...

    def generate(
        self,
        groups: list[SimilarityGroup],
        features: list[InputFeature],
        input_ids: list[str],
        history_context: PersonalHistoryContext | None = None,
        knowledge_context: AestheticKnowledgeContext | None = None,
    ) -> tuple[list[PossibleInterpretation], list[Insight]]: ...

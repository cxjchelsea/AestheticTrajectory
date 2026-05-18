from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.report import Insight


class MockInterpretationGenerator:
    def group(self, input_ids: list[str]) -> list[SimilarityGroup]:
        if len(input_ids) < 3:
            return []
        return [
            SimilarityGroup(
                groupId="group_mock_001",
                name="安静低密度组",
                inputIds=input_ids[:3],
                commonFeatures=["low_saturation", "low_density", "person_absent"],
                uncertainty="样本数量较少，该分组只表示本次输入中的相似结构。",
            )
        ]

    def interpret(self, evidence_refs: list[str]) -> list[PossibleInterpretation]:
        return [
            PossibleInterpretation(
                id="interpretation_mock_001",
                name="克制空间感",
                confidence=0.71,
                evidenceRefs=evidence_refs,
                uncertainty="也可能只是当前上传样本主题较集中。",
            )
        ]

    def insights(self, evidence_refs: list[str]) -> list[Insight]:
        return [
            Insight(
                insightId="insight_mock_001",
                title="你近期可能更容易被安静、低密度的结构吸引",
                observation="多个输入都出现低饱和、低元素密度和人物缺席。",
                evidenceRefs=evidence_refs,
                interpretation="这可能说明你现在更关注留白、秩序和克制的空间感。",
                uncertainty="它不是心理诊断，只是对本次样本的审美结构观察。",
                confidence=0.72,
            )
        ]

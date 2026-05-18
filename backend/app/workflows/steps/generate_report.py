from app.schemas.feature import InputFeature
from app.schemas.interpretation import PossibleInterpretation, SimilarityGroup
from app.schemas.report import Insight, ReportResponse


def generate_report(
    report_id: str,
    features: list[InputFeature],
    groups: list[SimilarityGroup],
    interpretations: list[PossibleInterpretation],
    insights: list[Insight],
) -> ReportResponse:
    return ReportResponse(
        reportId=report_id,
        title="近期审美观察报告",
        summary="这组输入呈现出低饱和、低密度、人物存在感较弱的共同倾向。",
        lowLevelFeatures=features,
        similarityGroups=groups,
        possibleInterpretations=interpretations,
        insights=insights,
        disclaimer="这是一份基于当前输入的审美观察，不是人格诊断、心理评估或长期画像。",
    )

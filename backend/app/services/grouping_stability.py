from itertools import combinations

from app.schemas.evaluation_maturity import (
    GROUPING_STABILITY_DISCLAIMER,
    GroupingPairDetail,
    GroupingStabilityResponse,
    GroupingStabilityTrace,
)
from app.schemas.input import AestheticInputResponse
from app.schemas.interpretation import SimilarityGroup
from app.schemas.report import ReportResponse
from app.workflows.steps.cluster_inputs import SIMILARITY_THRESHOLD, build_similarity_groups
from app.workflows.steps.generate_embeddings import generate_embeddings


def build_grouping_stability(
    report: ReportResponse,
    inputs: list[AestheticInputResponse],
) -> GroupingStabilityResponse:
    input_ids = [feature.input_id for feature in report.low_level_features]
    features = report.low_level_features

    if len(input_ids) < 3:
        return GroupingStabilityResponse(
            reportId=report.report_id,
            score=None,
            pairCount=0,
            consistentPairCount=0,
            persistedGroupCount=len(report.similarity_groups),
            recomputedGroupCount=0,
            message="样本数量少于 3，当前 clustering 规则不会生成分组。",
            disclaimer=GROUPING_STABILITY_DISCLAIMER,
        )

    input_by_id = {item.id: item for item in inputs}
    ordered_inputs = [input_by_id[input_id] for input_id in input_ids if input_id in input_by_id]
    if len(ordered_inputs) != len(input_ids):
        return GroupingStabilityResponse(
            reportId=report.report_id,
            score=None,
            pairCount=0,
            consistentPairCount=0,
            persistedGroupCount=len(report.similarity_groups),
            recomputedGroupCount=0,
            message="无法加载全部 input 记录，无法复算 clustering。",
            disclaimer=GROUPING_STABILITY_DISCLAIMER,
        )

    embeddings = generate_embeddings(ordered_inputs, features)
    recomputed_groups = build_similarity_groups(
        input_ids,
        features,
        embeddings,
        similarity_threshold=SIMILARITY_THRESHOLD,
    )
    pair_details = _compare_groups(input_ids, report.similarity_groups, recomputed_groups)
    pair_count = len(pair_details)
    consistent_pair_count = sum(1 for detail in pair_details if detail.consistent)
    score = consistent_pair_count / pair_count if pair_count else None

    return GroupingStabilityResponse(
        reportId=report.report_id,
        score=score,
        pairCount=pair_count,
        consistentPairCount=consistent_pair_count,
        persistedGroupCount=len(report.similarity_groups),
        recomputedGroupCount=len(recomputed_groups),
        pairDetails=pair_details,
        disclaimer=GROUPING_STABILITY_DISCLAIMER,
    )


def build_grouping_stability_trace(
    report: ReportResponse | None,
    inputs: list[AestheticInputResponse],
) -> GroupingStabilityTrace | None:
    if report is None:
        return None

    result = build_grouping_stability(report, inputs)
    if result.score is None:
        developer_message = result.message or "Grouping stability 未计算。"
    else:
        developer_message = (
            f"Persisted vs recomputed clustering pairwise consistency "
            f"{result.consistent_pair_count}/{result.pair_count} "
            f"(score={result.score:.2f})."
        )

    return GroupingStabilityTrace(
        reportId=report.report_id,
        score=result.score,
        pairCount=result.pair_count,
        consistentPairCount=result.consistent_pair_count,
        developerMessage=developer_message,
        disclaimer=result.disclaimer,
    )


def _compare_groups(
    input_ids: list[str],
    persisted_groups: list[SimilarityGroup],
    recomputed_groups: list[SimilarityGroup],
) -> list[GroupingPairDetail]:
    persisted_membership = _membership_map(persisted_groups)
    recomputed_membership = _membership_map(recomputed_groups)
    details: list[GroupingPairDetail] = []

    for left_id, right_id in combinations(input_ids, 2):
        persisted_same = _same_group(left_id, right_id, persisted_membership)
        recomputed_same = _same_group(left_id, right_id, recomputed_membership)
        details.append(
            GroupingPairDetail(
                inputIdA=left_id,
                inputIdB=right_id,
                persistedSameGroup=persisted_same,
                recomputedSameGroup=recomputed_same,
                consistent=persisted_same == recomputed_same,
            )
        )

    return details


def _membership_map(groups: list[SimilarityGroup]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for index, group in enumerate(groups):
        for input_id in group.input_ids:
            mapping[input_id] = index
    return mapping


def _same_group(left_id: str, right_id: str, membership: dict[str, int]) -> bool:
    if left_id not in membership or right_id not in membership:
        return False
    return membership[left_id] == membership[right_id]

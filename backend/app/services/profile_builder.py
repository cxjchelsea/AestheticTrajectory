from dataclasses import dataclass, field
from datetime import datetime
import re

from app.schemas.common import utc_now
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.profile import ProfileEvidence, ProfileItem, ProfileResponse, UserProfile
from app.schemas.report import ReportResponse


@dataclass
class EvidenceDraft:
    evidence_type: str
    evidence_id: str
    direction: str
    weight_delta: float
    note: str
    created_at: datetime


@dataclass
class ItemDraft:
    key: str
    label: str
    evidence: list[EvidenceDraft] = field(default_factory=list)
    last_seen_at: datetime | None = None


def build_profile_from_sources(
    user_id: str,
    reports: list[ReportResponse],
    feedback: list[InsightFeedbackResponse],
    now: datetime | None = None,
) -> ProfileResponse:
    timestamp = now or utc_now()
    drafts: dict[str, ItemDraft] = {}
    processed_feedback_ids: set[str] = set()

    for report in reports:
        for feature in report.low_level_features:
            for name, signal in feature.low_level_features.items():
                key = _profile_key(name, signal.value)
                draft = drafts.setdefault(key, ItemDraft(key=key, label=_label(name, signal.value)))
                draft.last_seen_at = timestamp
                draft.evidence.append(
                    EvidenceDraft(
                        evidence_type="feature",
                        evidence_id=f"feature_{feature.input_id}",
                        direction="positive",
                        weight_delta=0.2,
                        note=f"{name}={signal.value}: {signal.evidence[0]}",
                        created_at=timestamp,
                    )
                )

        for insight in report.insights:
            related_feedback = [
                item
                for item in feedback
                if item.insight_id == insight.insight_id and item.id not in processed_feedback_ids
            ]
            for item in related_feedback:
                processed_feedback_ids.add(item.id)
                key = _profile_key("insight", insight.title)
                draft = drafts.setdefault(key, ItemDraft(key=key, label=insight.title))
                draft.last_seen_at = item.created_at
                direction, weight_delta = _feedback_signal(item.rating)
                draft.evidence.append(
                    EvidenceDraft(
                        evidence_type="feedback",
                        evidence_id=item.id,
                        direction=direction,
                        weight_delta=weight_delta,
                        note=f"用户反馈 {item.rating}: {item.comment or insight.title}",
                        created_at=item.created_at,
                    )
                )

    for item in feedback:
        if item.id in processed_feedback_ids:
            continue
        key = _profile_key("feedback", item.insight_id)
        draft = drafts.setdefault(key, ItemDraft(key=key, label=f"反馈关联洞察 {item.insight_id}"))
        draft.last_seen_at = item.created_at
        direction, weight_delta = _feedback_signal(item.rating)
        draft.evidence.append(
            EvidenceDraft(
                evidence_type="feedback",
                evidence_id=item.id,
                direction=direction,
                weight_delta=weight_delta,
                note=f"用户反馈 {item.rating}: {item.comment or item.insight_id}",
                created_at=item.created_at,
            )
        )

    items = [
        _to_profile_item(f"profile_item_{user_id}_{index:03d}", draft)
        for index, draft in enumerate(drafts.values(), start=1)
    ]
    items = [item for item in items if item.evidence]
    if not items:
        return ProfileResponse(
            userId=user_id,
            profile=None,
            message="还没有足够证据生成轻量画像。",
        )

    summary = _summary(items)
    return ProfileResponse(
        userId=user_id,
        profile=UserProfile(
            id=f"profile_{user_id}",
            summary=summary,
            version="v2-b",
            items=items,
            updatedAt=timestamp,
        ),
    )


def _to_profile_item(item_id: str, draft: ItemDraft) -> ProfileItem:
    positive_count = sum(1 for evidence in draft.evidence if evidence.direction == "positive")
    negative_count = sum(1 for evidence in draft.evidence if evidence.direction == "negative")
    uncertain_count = sum(1 for evidence in draft.evidence if evidence.direction == "uncertain")
    feature_only = all(evidence.evidence_type == "feature" for evidence in draft.evidence)
    weight = max(-1.0, min(1.0, sum(evidence.weight_delta for evidence in draft.evidence)))

    if negative_count and weight <= 0:
        status = "rejected"
    elif uncertain_count and not positive_count:
        status = "uncertain"
    elif negative_count and positive_count:
        status = "recent" if weight > 0 else "uncertain"
    elif positive_count >= 2 or any(evidence.weight_delta >= 0.4 for evidence in draft.evidence):
        status = "stable"
    else:
        status = "recent"
    if feature_only and status == "stable":
        status = "recent"

    confidence = max(0.1, min(0.95, abs(weight) + min(len(draft.evidence), 3) * 0.1))
    return ProfileItem(
        id=item_id,
        key=draft.key,
        label=draft.label,
        status=status,
        weight=round(weight, 2),
        confidence=round(confidence, 2),
        sourceCount=len(draft.evidence),
        lastSeenAt=draft.last_seen_at or utc_now(),
        evidence=[
            ProfileEvidence(
                id=f"profile_evidence_{item_id}_{index:03d}",
                evidenceType=evidence.evidence_type,
                evidenceId=evidence.evidence_id,
                direction=evidence.direction,
                weightDelta=evidence.weight_delta,
                note=evidence.note,
                createdAt=evidence.created_at,
            )
            for index, evidence in enumerate(draft.evidence, start=1)
        ],
    )


def _feedback_signal(rating: str) -> tuple[str, float]:
    if rating == "very_me":
        return "positive", 0.4
    if rating == "somewhat_me":
        return "positive", 0.2
    if rating == "not_me":
        return "negative", -0.5
    return "uncertain", 0.0


def _profile_key(name: str, value: str) -> str:
    raw = f"{name}_{value}".lower()
    return re.sub(r"[^a-z0-9_]+", "_", raw).strip("_")[:120] or "unknown_profile_item"


def _label(name: str, value: str) -> str:
    return f"{name}: {value}"


def _summary(items: list[ProfileItem]) -> str:
    positive_items = [item.label for item in items if item.status in {"stable", "recent"} and item.weight > 0]
    if not positive_items:
        return "系统目前主要记录了被否定或不确定的审美解释，尚未形成正向轻量画像。"
    labels = "、".join(positive_items[:3])
    return f"系统观察到你近期输入中反复出现 {labels} 等审美倾向。"

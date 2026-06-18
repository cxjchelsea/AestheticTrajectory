from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AestheticTimelineEventModel
from app.repositories.memory_store import MemoryStore
from app.schemas.common import new_id, utc_now
from app.schemas.timeline import TimelineEvent, TimelineEventDraft, TimelineListResponse


TIMELINE_DISCLAIMER = "审美时间轴只汇总已有报告与反馈中的可追溯变化，不是人格、心理或能力判断。"


def _to_event(draft: TimelineEventDraft, event_id: str | None = None) -> TimelineEvent:
    now = utc_now()
    return TimelineEvent(
        id=event_id or new_id("timeline"),
        userId=draft.user_id,
        eventType=draft.event_type,
        title=draft.title,
        description=draft.description,
        relatedReportIds=draft.related_report_ids,
        relatedInsightIds=draft.related_insight_ids,
        relatedFeedbackIds=draft.related_feedback_ids,
        evidence=draft.evidence,
        occurredAt=draft.occurred_at,
        createdAt=now,
    )


def _event_from_model(row: AestheticTimelineEventModel) -> TimelineEvent:
    from app.schemas.timeline import TimelineEvidence

    return TimelineEvent(
        id=row.id,
        userId=row.user_id,
        eventType=row.event_type,
        title=row.title,
        description=row.description,
        relatedReportIds=list(row.related_report_ids_json or []),
        relatedInsightIds=list(row.related_insight_ids_json or []),
        relatedFeedbackIds=list(row.related_feedback_ids_json or []),
        evidence=TimelineEvidence.model_validate(row.evidence_json),
        occurredAt=row.occurred_at,
        createdAt=row.created_at,
    )


class TimelineRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def append_events(self, drafts: list[TimelineEventDraft]) -> list[TimelineEvent]:
        saved: list[TimelineEvent] = []
        for draft in drafts:
            if self._dedupe_exists(draft.user_id, draft.evidence.dedupe_key):
                continue
            event = _to_event(draft)
            self.store.timeline_events[event.id] = event
            self.store.timeline_dedupe_keys.add((draft.user_id, draft.evidence.dedupe_key))
            saved.append(event)
        return saved

    def _dedupe_exists(self, user_id: str, dedupe_key: str) -> bool:
        return (user_id, dedupe_key) in self.store.timeline_dedupe_keys

    def list_by_user(
        self,
        user_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
    ) -> TimelineListResponse:
        events = [
            event
            for event in self.store.timeline_events.values()
            if event.user_id == user_id
            and (occurred_from is None or event.occurred_at >= occurred_from)
            and (occurred_to is None or event.occurred_at <= occurred_to)
        ]
        events.sort(key=lambda item: (item.occurred_at, item.id), reverse=True)
        total = len(events)
        page = events[offset : offset + limit]
        message = None if page else "还没有可追溯的审美时间轴事件。完成更多分析后会逐步积累。"
        return TimelineListResponse(
            userId=user_id,
            events=page,
            total=total,
            limit=limit,
            offset=offset,
            message=message,
            disclaimer=TIMELINE_DISCLAIMER,
        )

    def list_decline_labels(self, user_id: str) -> set[str]:
        labels: set[str] = set()
        for event in self.store.timeline_events.values():
            if event.user_id != user_id:
                continue
            if event.event_type != "interpretation_decline":
                continue
            labels.add(event.title)
        return labels


class DatabaseTimelineRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def append_events(self, drafts: list[TimelineEventDraft]) -> list[TimelineEvent]:
        saved: list[TimelineEvent] = []
        for draft in drafts:
            existing = self.session.scalars(
                select(AestheticTimelineEventModel).where(
                    AestheticTimelineEventModel.user_id == draft.user_id,
                    AestheticTimelineEventModel.dedupe_key == draft.evidence.dedupe_key,
                )
            ).first()
            if existing is not None:
                continue
            event = _to_event(draft)
            row = AestheticTimelineEventModel(
                id=event.id,
                user_id=event.user_id,
                event_type=event.event_type,
                title=event.title,
                description=event.description,
                related_report_ids_json=event.related_report_ids,
                related_insight_ids_json=event.related_insight_ids,
                related_feedback_ids_json=event.related_feedback_ids,
                evidence_json=event.evidence.model_dump(by_alias=True),
                dedupe_key=event.evidence.dedupe_key,
                occurred_at=event.occurred_at,
                created_at=event.created_at,
            )
            self.session.add(row)
            try:
                self.session.flush()
            except IntegrityError:
                self.session.rollback()
                continue
            saved.append(event)
        return saved

    def list_by_user(
        self,
        user_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        occurred_from: datetime | None = None,
        occurred_to: datetime | None = None,
    ) -> TimelineListResponse:
        query = select(AestheticTimelineEventModel).where(AestheticTimelineEventModel.user_id == user_id)
        if occurred_from is not None:
            query = query.where(AestheticTimelineEventModel.occurred_at >= occurred_from)
        if occurred_to is not None:
            query = query.where(AestheticTimelineEventModel.occurred_at <= occurred_to)
        rows = self.session.scalars(
            query.order_by(AestheticTimelineEventModel.occurred_at.desc(), AestheticTimelineEventModel.id.desc())
        ).all()
        total = len(rows)
        page = [_event_from_model(row) for row in rows[offset : offset + limit]]
        message = None if page else "还没有可追溯的审美时间轴事件。完成更多分析后会逐步积累。"
        return TimelineListResponse(
            userId=user_id,
            events=page,
            total=total,
            limit=limit,
            offset=offset,
            message=message,
            disclaimer=TIMELINE_DISCLAIMER,
        )

    def list_decline_labels(self, user_id: str) -> set[str]:
        rows = self.session.scalars(
            select(AestheticTimelineEventModel.title).where(
                AestheticTimelineEventModel.user_id == user_id,
                AestheticTimelineEventModel.event_type == "interpretation_decline",
            )
        ).all()
        return set(rows)

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persistence import ExternalContextItemModel, ExternalImportBatchModel
from app.repositories.memory_store import MemoryStore
from app.schemas.common import new_id, utc_now
from app.schemas.external_context import (
    CreateExternalImportRequest,
    ExternalContextItem,
    ExternalImportBatch,
    ExternalImportListResponse,
    EXTERNAL_CONTEXT_DISCLAIMER,
)


def _item_from_model(row: ExternalContextItemModel) -> ExternalContextItem:
    return ExternalContextItem(
        id=row.id,
        batchId=row.batch_id,
        userId=row.user_id,
        title=row.title,
        snippet=row.snippet,
        sourceUri=row.source_uri,
        tags=list(row.tags_json or []),
        createdAt=row.created_at,
    )


def _batch_from_model(row: ExternalImportBatchModel, items: list[ExternalContextItem]) -> ExternalImportBatch:
    return ExternalImportBatch(
        id=row.id,
        userId=row.user_id,
        sourceSystem=row.source_system,
        status=row.status,
        itemCount=row.item_count,
        items=items,
        confirmedAt=row.confirmed_at,
        createdAt=row.created_at,
        disclaimer=EXTERNAL_CONTEXT_DISCLAIMER,
    )


class ExternalImportRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def create_batch(self, user_id: str, request: CreateExternalImportRequest) -> ExternalImportBatch:
        now = utc_now()
        batch_id = new_id("import_batch")
        items: list[ExternalContextItem] = []
        for draft in request.items:
            item = ExternalContextItem(
                id=new_id("external_ctx"),
                batchId=batch_id,
                userId=user_id,
                title=draft.title,
                snippet=draft.snippet,
                sourceUri=draft.source_uri,
                tags=draft.tags,
                createdAt=now,
            )
            self.store.external_context_items[item.id] = item
            items.append(item)

        batch = ExternalImportBatch(
            id=batch_id,
            userId=user_id,
            sourceSystem=request.source_system,
            status="pending_confirmation",
            itemCount=len(items),
            items=items,
            createdAt=now,
            disclaimer=EXTERNAL_CONTEXT_DISCLAIMER,
        )
        self.store.external_import_batches[batch_id] = batch
        return batch

    def get_batch(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        batch = self.store.external_import_batches.get(batch_id)
        if batch is None or batch.user_id != user_id:
            return None
        items = [
            item
            for item in self.store.external_context_items.values()
            if item.batch_id == batch_id
        ]
        return batch.model_copy(update={"items": items})

    def list_batches(self, user_id: str) -> ExternalImportListResponse:
        batches = [
            self.get_batch(user_id, batch_id) or batch
            for batch_id, batch in self.store.external_import_batches.items()
            if batch.user_id == user_id
        ]
        batches = [batch for batch in batches if batch is not None]
        batches.sort(key=lambda item: item.created_at, reverse=True)
        return ExternalImportListResponse(userId=user_id, batches=batches, total=len(batches))

    def confirm_batch(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        batch = self.get_batch(user_id, batch_id)
        if batch is None or batch.status != "pending_confirmation":
            return None
        updated = batch.model_copy(update={"status": "confirmed", "confirmedAt": utc_now()})
        self.store.external_import_batches[batch_id] = updated
        return updated

    def reject_batch(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        batch = self.get_batch(user_id, batch_id)
        if batch is None or batch.status != "pending_confirmation":
            return None
        updated = batch.model_copy(update={"status": "rejected"})
        self.store.external_import_batches[batch_id] = updated
        return updated

    def list_confirmed_items(self, user_id: str) -> list[ExternalContextItem]:
        confirmed_batch_ids = {
            batch.id
            for batch in self.store.external_import_batches.values()
            if batch.user_id == user_id and batch.status == "confirmed"
        }
        return [
            item
            for item in self.store.external_context_items.values()
            if item.user_id == user_id and item.batch_id in confirmed_batch_ids
        ]


class DatabaseExternalImportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _items_for_batch(self, batch_id: str) -> list[ExternalContextItem]:
        rows = self.session.scalars(
            select(ExternalContextItemModel).where(ExternalContextItemModel.batch_id == batch_id)
        ).all()
        return [_item_from_model(row) for row in rows]

    def create_batch(self, user_id: str, request: CreateExternalImportRequest) -> ExternalImportBatch:
        now = utc_now()
        batch_id = new_id("import_batch")
        items: list[ExternalContextItem] = []
        for draft in request.items:
            item_id = new_id("external_ctx")
            row = ExternalContextItemModel(
                id=item_id,
                batch_id=batch_id,
                user_id=user_id,
                title=draft.title,
                snippet=draft.snippet,
                source_uri=draft.source_uri,
                tags_json=draft.tags,
                created_at=now,
            )
            self.session.add(row)
            items.append(_item_from_model(row))

        batch_row = ExternalImportBatchModel(
            id=batch_id,
            user_id=user_id,
            source_system=request.source_system,
            status="pending_confirmation",
            item_count=len(items),
            confirmed_at=None,
            created_at=now,
        )
        self.session.add(batch_row)
        self.session.flush()
        return _batch_from_model(batch_row, items)

    def get_batch(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        row = self.session.get(ExternalImportBatchModel, batch_id)
        if row is None or row.user_id != user_id:
            return None
        return _batch_from_model(row, self._items_for_batch(batch_id))

    def list_batches(self, user_id: str) -> ExternalImportListResponse:
        rows = self.session.scalars(
            select(ExternalImportBatchModel)
            .where(ExternalImportBatchModel.user_id == user_id)
            .order_by(ExternalImportBatchModel.created_at.desc())
        ).all()
        batches = [_batch_from_model(row, self._items_for_batch(row.id)) for row in rows]
        return ExternalImportListResponse(userId=user_id, batches=batches, total=len(batches))

    def confirm_batch(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        row = self.session.get(ExternalImportBatchModel, batch_id)
        if row is None or row.user_id != user_id or row.status != "pending_confirmation":
            return None
        row.status = "confirmed"
        row.confirmed_at = utc_now()
        self.session.flush()
        return _batch_from_model(row, self._items_for_batch(batch_id))

    def reject_batch(self, user_id: str, batch_id: str) -> ExternalImportBatch | None:
        row = self.session.get(ExternalImportBatchModel, batch_id)
        if row is None or row.user_id != user_id or row.status != "pending_confirmation":
            return None
        row.status = "rejected"
        self.session.flush()
        return _batch_from_model(row, self._items_for_batch(batch_id))

    def list_confirmed_items(self, user_id: str) -> list[ExternalContextItem]:
        batch_rows = self.session.scalars(
            select(ExternalImportBatchModel).where(
                ExternalImportBatchModel.user_id == user_id,
                ExternalImportBatchModel.status == "confirmed",
            )
        ).all()
        batch_ids = {row.id for row in batch_rows}
        if not batch_ids:
            return []
        rows = self.session.scalars(
            select(ExternalContextItemModel).where(ExternalContextItemModel.batch_id.in_(batch_ids))
        ).all()
        return [_item_from_model(row) for row in rows]

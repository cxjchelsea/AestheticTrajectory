from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import UserModel, UserSessionModel
from app.repositories.memory_store import MemoryStore, store
from app.schemas.common import new_id


@dataclass(frozen=True)
class SessionRecord:
    id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_seen_at: datetime


class MemorySessionRepository:
    def __init__(self, memory_store: MemoryStore = store) -> None:
        self.store = memory_store
        self._ensure_dev_user()

    def get_valid_session(self, session_id: str, now: datetime) -> SessionRecord | None:
        raw = self.store.user_sessions.get(session_id)
        if raw is None:
            return None
        record = _session_from_raw(raw)
        if record.expires_at <= now:
            del self.store.user_sessions[session_id]
            return None
        return record

    def touch_session(self, session_id: str, now: datetime) -> SessionRecord | None:
        record = self.get_valid_session(session_id, now)
        if record is None:
            return None
        updated = SessionRecord(
            id=record.id,
            user_id=record.user_id,
            created_at=record.created_at,
            expires_at=record.expires_at,
            last_seen_at=now,
        )
        self.store.user_sessions[session_id] = _session_to_raw(updated)
        return updated

    def create_user_with_session(self, ttl_days: int, now: datetime) -> SessionRecord:
        user_id = new_id("user")
        self._ensure_user(user_id, now)
        return self.create_session_for_user(user_id, ttl_days, now)

    def create_session_for_user(self, user_id: str, ttl_days: int, now: datetime) -> SessionRecord:
        self._ensure_user(user_id, now)
        session_id = new_id("sess")
        record = SessionRecord(
            id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(days=ttl_days),
            last_seen_at=now,
        )
        self.store.user_sessions[session_id] = _session_to_raw(record)
        return record

    def _ensure_dev_user(self) -> None:
        return

    def _ensure_user(self, user_id: str, now: datetime) -> None:
        return


class DatabaseSessionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_valid_session(self, session_id: str, now: datetime) -> SessionRecord | None:
        row = self.session.get(UserSessionModel, session_id)
        if row is None or row.expires_at <= now:
            return None
        return _session_from_model(row)

    def touch_session(self, session_id: str, now: datetime) -> SessionRecord | None:
        row = self.session.get(UserSessionModel, session_id)
        if row is None or row.expires_at <= now:
            return None
        row.last_seen_at = now
        self.session.flush()
        return _session_from_model(row)

    def create_user_with_session(self, ttl_days: int, now: datetime) -> SessionRecord:
        user_id = new_id("user")
        self._ensure_user(user_id, now)
        return self.create_session_for_user(user_id, ttl_days, now)

    def create_session_for_user(self, user_id: str, ttl_days: int, now: datetime) -> SessionRecord:
        self._ensure_user(user_id, now)
        session_id = new_id("sess")
        row = UserSessionModel(
            id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(days=ttl_days),
            last_seen_at=now,
        )
        self.session.add(row)
        self.session.flush()
        return _session_from_model(row)

    def _ensure_user(self, user_id: str, now: datetime) -> None:
        if self.session.get(UserModel, user_id) is None:
            try:
                self.session.add(
                    UserModel(
                        id=user_id,
                        anonymous_id=user_id,
                        created_at=now,
                        updated_at=now,
                    )
                )
                self.session.flush()
            except IntegrityError:
                self.session.rollback()
                if self.session.get(UserModel, user_id) is None:
                    raise


def _session_from_model(row: UserSessionModel) -> SessionRecord:
    return SessionRecord(
        id=row.id,
        user_id=row.user_id,
        created_at=row.created_at,
        expires_at=row.expires_at,
        last_seen_at=row.last_seen_at,
    )


def _session_from_raw(raw: dict[str, object]) -> SessionRecord:
    return SessionRecord(
        id=str(raw["id"]),
        user_id=str(raw["user_id"]),
        created_at=raw["created_at"],  # type: ignore[arg-type]
        expires_at=raw["expires_at"],  # type: ignore[arg-type]
        last_seen_at=raw["last_seen_at"],  # type: ignore[arg-type]
    )


def _session_to_raw(record: SessionRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "created_at": record.created_at,
        "expires_at": record.expires_at,
        "last_seen_at": record.last_seen_at,
    }

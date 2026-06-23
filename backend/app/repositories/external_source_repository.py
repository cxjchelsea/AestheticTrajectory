from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persistence import ExternalOAuthStateModel, ExternalSourceConnectionModel
from app.repositories.memory_store import MemoryStore
from app.schemas.common import new_id, utc_now
from app.schemas.external_source import ExternalOAuthState, ExternalSourceConnection


def _public_connection(payload: dict[str, object]) -> ExternalSourceConnection:
    return ExternalSourceConnection(
        id=str(payload["id"]),
        userId=str(payload["user_id"]),
        provider=str(payload["provider"]),
        status=str(payload["status"]),
        scopes=list(payload.get("scopes") or []),
        resourceUri=payload.get("resource_uri"),
        tokenExpiresAt=payload.get("token_expires_at"),
        lastConnectedAt=payload.get("last_connected_at"),
        lastError=payload.get("last_error"),
        createdAt=payload["created_at"],
        updatedAt=payload["updated_at"],
    )


def _connection_from_model(row: ExternalSourceConnectionModel) -> ExternalSourceConnection:
    return ExternalSourceConnection(
        id=row.id,
        userId=row.user_id,
        provider=row.provider,
        status=row.status,
        scopes=list(row.scopes_json or []),
        resourceUri=row.resource_uri,
        tokenExpiresAt=row.token_expires_at,
        lastConnectedAt=row.last_connected_at,
        lastError=row.last_error,
        createdAt=row.created_at,
        updatedAt=row.updated_at,
    )


def _state_from_model(row: ExternalOAuthStateModel) -> ExternalOAuthState:
    return ExternalOAuthState(
        state=row.state,
        userId=row.user_id,
        provider=row.provider,
        codeVerifier=row.code_verifier,
        redirectAfter=row.redirect_after,
        createdAt=row.created_at,
        expiresAt=row.expires_at,
    )


class ExternalSourceRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def list_connections(self, user_id: str) -> list[ExternalSourceConnection]:
        rows = [
            payload
            for payload in self.store.external_source_connections.values()
            if payload["user_id"] == user_id
        ]
        rows.sort(key=lambda item: item["updated_at"], reverse=True)
        return [_public_connection(row) for row in rows]

    def get_connection(self, user_id: str, provider: str) -> ExternalSourceConnection | None:
        payload = self._get_payload(user_id, provider)
        return _public_connection(payload) if payload is not None else None

    def _get_payload(self, user_id: str, provider: str) -> dict[str, object] | None:
        for payload in self.store.external_source_connections.values():
            if payload["user_id"] == user_id and payload["provider"] == provider:
                return payload
        return None

    def get_access_token(self, user_id: str, provider: str) -> str | None:
        payload = self._get_payload(user_id, provider)
        if payload is None or payload["status"] != "connected":
            return None
        token = payload.get("access_token_ciphertext")
        return str(token) if token else None

    def upsert_connection(
        self,
        *,
        user_id: str,
        provider: str,
        status: str,
        scopes: list[str],
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expires_at: datetime | None = None,
        resource_uri: str | None = None,
        last_error: str | None = None,
    ) -> ExternalSourceConnection:
        now = utc_now()
        payload = self._get_payload(user_id, provider)
        if payload is None:
            payload = {
                "id": new_id("external_connection"),
                "user_id": user_id,
                "provider": provider,
                "created_at": now,
            }
            self.store.external_source_connections[str(payload["id"])] = payload
        payload.update(
            {
                "status": status,
                "scopes": scopes,
                "access_token_ciphertext": access_token,
                "refresh_token_ciphertext": refresh_token,
                "token_expires_at": token_expires_at,
                "resource_uri": resource_uri,
                "last_connected_at": now if status == "connected" else payload.get("last_connected_at"),
                "last_error": last_error,
                "updated_at": now,
            }
        )
        return _public_connection(payload)

    def disconnect(self, user_id: str, provider: str) -> ExternalSourceConnection | None:
        payload = self._get_payload(user_id, provider)
        if payload is None:
            return None
        now = utc_now()
        payload.update(
            {
                "status": "disconnected",
                "access_token_ciphertext": None,
                "refresh_token_ciphertext": None,
                "token_expires_at": None,
                "updated_at": now,
            }
        )
        return _public_connection(payload)

    def save_oauth_state(self, state: ExternalOAuthState) -> ExternalOAuthState:
        self.store.external_oauth_states[state.state] = state
        return state

    def consume_oauth_state(self, user_id: str, provider: str, state: str) -> ExternalOAuthState | None:
        record = self.store.external_oauth_states.pop(state, None)
        if record is None or record.user_id != user_id or record.provider != provider:
            return None
        if record.expires_at < utc_now():
            return None
        return record


class DatabaseExternalSourceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_connections(self, user_id: str) -> list[ExternalSourceConnection]:
        rows = self.session.scalars(
            select(ExternalSourceConnectionModel)
            .where(ExternalSourceConnectionModel.user_id == user_id)
            .order_by(ExternalSourceConnectionModel.updated_at.desc())
        ).all()
        return [_connection_from_model(row) for row in rows]

    def get_connection(self, user_id: str, provider: str) -> ExternalSourceConnection | None:
        row = self._get_row(user_id, provider)
        return _connection_from_model(row) if row is not None else None

    def _get_row(self, user_id: str, provider: str) -> ExternalSourceConnectionModel | None:
        return self.session.scalars(
            select(ExternalSourceConnectionModel).where(
                ExternalSourceConnectionModel.user_id == user_id,
                ExternalSourceConnectionModel.provider == provider,
            )
        ).first()

    def get_access_token(self, user_id: str, provider: str) -> str | None:
        row = self._get_row(user_id, provider)
        if row is None or row.status != "connected":
            return None
        return row.access_token_ciphertext

    def upsert_connection(
        self,
        *,
        user_id: str,
        provider: str,
        status: str,
        scopes: list[str],
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expires_at: datetime | None = None,
        resource_uri: str | None = None,
        last_error: str | None = None,
    ) -> ExternalSourceConnection:
        now = utc_now()
        row = self._get_row(user_id, provider)
        if row is None:
            row = ExternalSourceConnectionModel(
                id=new_id("external_connection"),
                user_id=user_id,
                provider=provider,
                created_at=now,
                updated_at=now,
                status=status,
                scopes_json=scopes,
            )
            self.session.add(row)
        row.status = status
        row.scopes_json = scopes
        row.access_token_ciphertext = access_token
        row.refresh_token_ciphertext = refresh_token
        row.token_expires_at = token_expires_at
        row.resource_uri = resource_uri
        row.last_error = last_error
        if status == "connected":
            row.last_connected_at = now
        row.updated_at = now
        self.session.flush()
        return _connection_from_model(row)

    def disconnect(self, user_id: str, provider: str) -> ExternalSourceConnection | None:
        row = self._get_row(user_id, provider)
        if row is None:
            return None
        row.status = "disconnected"
        row.access_token_ciphertext = None
        row.refresh_token_ciphertext = None
        row.token_expires_at = None
        row.updated_at = utc_now()
        self.session.flush()
        return _connection_from_model(row)

    def save_oauth_state(self, state: ExternalOAuthState) -> ExternalOAuthState:
        row = ExternalOAuthStateModel(
            state=state.state,
            user_id=state.user_id,
            provider=state.provider,
            code_verifier=state.code_verifier,
            redirect_after=state.redirect_after,
            created_at=state.created_at,
            expires_at=state.expires_at,
        )
        self.session.add(row)
        self.session.flush()
        return state

    def consume_oauth_state(self, user_id: str, provider: str, state: str) -> ExternalOAuthState | None:
        row = self.session.get(ExternalOAuthStateModel, state)
        if row is None or row.user_id != user_id or row.provider != provider:
            return None
        record = _state_from_model(row)
        self.session.delete(row)
        self.session.flush()
        if record.expires_at < utc_now():
            return None
        return record

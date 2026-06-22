from app.core.auth import DEV_USER_ID
from app.core.config import settings
from app.repositories.session_repository import SessionRecord
from app.schemas.common import utc_now
from app.schemas.session import SessionBootstrapResponse, SessionMeResponse


class SessionService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def bootstrap(self, existing_session_id: str | None) -> tuple[SessionBootstrapResponse, bool]:
        if settings.auth_mode == "dev":
            return (
                SessionBootstrapResponse(
                    userId=DEV_USER_ID,
                    sessionToken="",
                    authMode="dev",
                ),
                False,
            )

        now = utc_now()
        if existing_session_id:
            record = self.repository.touch_session(existing_session_id, now)
            if record is not None:
                return self._to_bootstrap(record), False

        record = self.repository.create_user_with_session(settings.session_ttl_days, now)
        return self._to_bootstrap(record), True

    def get_me(self, existing_session_id: str | None) -> SessionMeResponse:
        auth_mode = settings.auth_mode
        if auth_mode == "dev":
            from app.core.auth import DEV_USER_ID

            return SessionMeResponse(
                userId=DEV_USER_ID,
                authMode=auth_mode,
                sessionPresent=existing_session_id is not None,
            )

        if existing_session_id is None:
            return SessionMeResponse(userId="", authMode=auth_mode, sessionPresent=False)

        record = self.repository.get_valid_session(existing_session_id, utc_now())
        if record is None:
            return SessionMeResponse(userId="", authMode=auth_mode, sessionPresent=False)

        return SessionMeResponse(
            userId=record.user_id,
            authMode=auth_mode,
            sessionPresent=True,
        )

    def resolve_session(self, session_id: str | None) -> SessionRecord | None:
        if session_id is None:
            return None
        return self.repository.get_valid_session(session_id, utc_now())

    def _to_bootstrap(self, record: SessionRecord) -> SessionBootstrapResponse:
        return SessionBootstrapResponse(
            userId=record.user_id,
            sessionToken=record.id,
            authMode=settings.auth_mode,
        )

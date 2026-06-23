import base64
from datetime import timedelta
import hashlib
import secrets

from app.core.config import settings
from app.repositories.external_import_repository import DatabaseExternalImportRepository, ExternalImportRepository
from app.repositories.external_source_repository import DatabaseExternalSourceRepository, ExternalSourceRepository
from app.schemas.common import utc_now
from app.schemas.external_context import CreateExternalImportRequest, ExternalImportBatch
from app.schemas.external_source import (
    ExternalOAuthState,
    ExternalSourceConnectResponse,
    ExternalSourceConnection,
    ExternalSourceListResponse,
    ExternalSourceStatusResponse,
    PreviewExternalImportRequest,
)
from app.services.external_source_connectors import get_external_source_connector


class ExternalSourceDisabledError(ValueError):
    pass


class ExternalSourceAuthorizationError(ValueError):
    pass


class ExternalSourceConnectionRequiredError(ValueError):
    pass


class ExternalSourceService:
    def __init__(
        self,
        source_repository: ExternalSourceRepository | DatabaseExternalSourceRepository,
        import_repository: ExternalImportRepository | DatabaseExternalImportRepository,
    ) -> None:
        self.source_repository = source_repository
        self.import_repository = import_repository

    def list_sources(self, user_id: str) -> ExternalSourceListResponse:
        connections = self.source_repository.list_connections(user_id)
        return ExternalSourceListResponse(
            userId=user_id,
            runtime=settings.external_source_runtime,
            connections=connections,
            total=len(connections),
        )

    def get_status(self, user_id: str, provider: str) -> ExternalSourceStatusResponse:
        runtime = settings.external_source_runtime
        return ExternalSourceStatusResponse(
            provider=provider,
            runtime=runtime,
            enabled=runtime != "disabled",
            connection=self.source_repository.get_connection(user_id, provider),
        )

    def start_connect(self, user_id: str, provider: str) -> ExternalSourceConnectResponse:
        runtime = settings.external_source_runtime
        if runtime == "disabled":
            raise ExternalSourceDisabledError("EXTERNAL_SOURCE_RUNTIME=disabled")

        connector = get_external_source_connector(runtime, provider)
        state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(48)
        code_challenge = _pkce_challenge(code_verifier)
        redirect_uri = _redirect_uri(user_id, provider)
        now = utc_now()

        self.source_repository.save_oauth_state(
            ExternalOAuthState(
                state=state,
                userId=user_id,
                provider=provider,
                codeVerifier=code_verifier,
                createdAt=now,
                expiresAt=now + timedelta(minutes=10),
            )
        )
        self.source_repository.upsert_connection(
            user_id=user_id,
            provider=provider,
            status="pending_authorization",
            scopes=connector.required_scopes,
        )

        authorization_url = connector.build_authorization_url(
            user_id=user_id,
            state=state,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
        )
        return ExternalSourceConnectResponse(
            provider=provider,
            authorizationUrl=authorization_url,
            state=state,
            status="pending_authorization",
        )

    def complete_callback(
        self,
        *,
        user_id: str,
        provider: str,
        code: str,
        state: str,
    ) -> ExternalSourceConnection:
        runtime = settings.external_source_runtime
        if runtime == "disabled":
            raise ExternalSourceDisabledError("EXTERNAL_SOURCE_RUNTIME=disabled")

        oauth_state = self.source_repository.consume_oauth_state(user_id, provider, state)
        if oauth_state is None:
            raise ExternalSourceAuthorizationError("OAuth state is invalid or expired")

        connector = get_external_source_connector(runtime, provider)
        token = connector.exchange_code(
            code=code,
            code_verifier=oauth_state.code_verifier,
            redirect_uri=_redirect_uri(user_id, provider),
        )
        return self.source_repository.upsert_connection(
            user_id=user_id,
            provider=provider,
            status="connected",
            scopes=token.scopes,
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_expires_at=token.expires_at,
            resource_uri=token.resource_uri,
        )

    def disconnect(self, user_id: str, provider: str) -> ExternalSourceConnection | None:
        return self.source_repository.disconnect(user_id, provider)

    def preview_import(
        self,
        user_id: str,
        provider: str,
        request: PreviewExternalImportRequest,
    ) -> ExternalImportBatch:
        runtime = settings.external_source_runtime
        if runtime == "disabled":
            raise ExternalSourceDisabledError("EXTERNAL_SOURCE_RUNTIME=disabled")

        access_token = self.source_repository.get_access_token(user_id, provider)
        if access_token is None:
            raise ExternalSourceConnectionRequiredError("External source connection is required")

        connector = get_external_source_connector(runtime, provider)
        drafts = connector.list_items(access_token=access_token, limit=request.limit)
        return self.import_repository.create_batch(
            user_id,
            CreateExternalImportRequest(sourceSystem=provider, items=drafts),
        )


def _redirect_uri(user_id: str, provider: str) -> str:
    configured = settings.external_source_redirect_uri
    if configured:
        return configured.format(user_id=user_id, provider=provider)
    return f"/api/users/{user_id}/external-sources/{provider}/oauth/callback"


def _pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ExternalSourceConnectionStatus = Literal[
    "pending_authorization",
    "connected",
    "disconnected",
    "expired",
    "revoked",
    "failed",
]


class ExternalSourceConnection(BaseModel):
    id: str
    user_id: str = Field(alias="userId")
    provider: str
    status: ExternalSourceConnectionStatus
    scopes: list[str] = Field(default_factory=list)
    resource_uri: str | None = Field(default=None, alias="resourceUri")
    token_expires_at: datetime | None = Field(default=None, alias="tokenExpiresAt")
    last_connected_at: datetime | None = Field(default=None, alias="lastConnectedAt")
    last_error: str | None = Field(default=None, alias="lastError")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class ExternalOAuthState(BaseModel):
    state: str
    user_id: str = Field(alias="userId")
    provider: str
    code_verifier: str = Field(alias="codeVerifier")
    redirect_after: str | None = Field(default=None, alias="redirectAfter")
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class ExternalSourceConnectResponse(BaseModel):
    provider: str
    authorization_url: str = Field(alias="authorizationUrl")
    state: str
    status: ExternalSourceConnectionStatus

    model_config = {"populate_by_name": True}


class ExternalSourceListResponse(BaseModel):
    user_id: str = Field(alias="userId")
    runtime: str
    connections: list[ExternalSourceConnection]
    total: int

    model_config = {"populate_by_name": True}


class PreviewExternalImportRequest(BaseModel):
    limit: int = Field(default=3, ge=1, le=10)


class ExternalSourceStatusResponse(BaseModel):
    provider: str
    runtime: str
    enabled: bool
    connection: ExternalSourceConnection | None = None

    model_config = {"populate_by_name": True}

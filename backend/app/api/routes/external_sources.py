from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_external_source_service, require_user_scope
from app.schemas.external_context import ExternalImportBatch
from app.schemas.external_source import (
    ExternalSourceConnectResponse,
    ExternalSourceConnection,
    ExternalSourceListResponse,
    ExternalSourceStatusResponse,
    PreviewExternalImportRequest,
)
from app.services.external_source_service import (
    ExternalSourceAuthorizationError,
    ExternalSourceConnectionRequiredError,
    ExternalSourceDisabledError,
    ExternalSourceService,
)


router = APIRouter(tags=["external-sources"])


@router.get("/users/{user_id}/external-sources", response_model=ExternalSourceListResponse)
def list_external_sources(
    user_id: str,
    service: ExternalSourceService = Depends(get_external_source_service),
    _: str = Depends(require_user_scope),
) -> ExternalSourceListResponse:
    return service.list_sources(user_id)


@router.get("/users/{user_id}/external-sources/{provider}", response_model=ExternalSourceStatusResponse)
def get_external_source_status(
    user_id: str,
    provider: str,
    service: ExternalSourceService = Depends(get_external_source_service),
    _: str = Depends(require_user_scope),
) -> ExternalSourceStatusResponse:
    return service.get_status(user_id, provider)


@router.post("/users/{user_id}/external-sources/{provider}/connect", response_model=ExternalSourceConnectResponse)
def connect_external_source(
    user_id: str,
    provider: str,
    service: ExternalSourceService = Depends(get_external_source_service),
    _: str = Depends(require_user_scope),
) -> ExternalSourceConnectResponse:
    try:
        return service.start_connect(user_id, provider)
    except (ExternalSourceDisabledError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/users/{user_id}/external-sources/{provider}/oauth/callback", response_model=ExternalSourceConnection)
def external_source_oauth_callback(
    user_id: str,
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    service: ExternalSourceService = Depends(get_external_source_service),
    _: str = Depends(require_user_scope),
) -> ExternalSourceConnection:
    try:
        return service.complete_callback(user_id=user_id, provider=provider, code=code, state=state)
    except (ExternalSourceAuthorizationError, ExternalSourceDisabledError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/users/{user_id}/external-sources/{provider}/disconnect", response_model=ExternalSourceConnection)
def disconnect_external_source(
    user_id: str,
    provider: str,
    service: ExternalSourceService = Depends(get_external_source_service),
    _: str = Depends(require_user_scope),
) -> ExternalSourceConnection:
    connection = service.disconnect(user_id, provider)
    if connection is None:
        raise HTTPException(status_code=404, detail="External source connection not found")
    return connection


@router.post("/users/{user_id}/external-sources/{provider}/imports/preview", response_model=ExternalImportBatch)
def preview_external_import(
    user_id: str,
    provider: str,
    request: PreviewExternalImportRequest,
    service: ExternalSourceService = Depends(get_external_source_service),
    _: str = Depends(require_user_scope),
) -> ExternalImportBatch:
    try:
        return service.preview_import(user_id, provider, request)
    except (ExternalSourceConnectionRequiredError, ExternalSourceDisabledError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

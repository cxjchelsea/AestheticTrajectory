from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_observation_service, require_user_scope
from app.schemas.agent import AgentActionListResponse, CreateObservationRequest, ObservationSession
from app.schemas.external_context import CreateExternalImportRequest, ExternalImportBatch, ExternalImportListResponse
from app.services.observation_service import ObservationService

router = APIRouter(tags=["observations"])


@router.post("/users/{user_id}/observations", response_model=ObservationSession)
def create_observation(
    user_id: str,
    request: CreateObservationRequest,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ObservationSession:
    return service.create_observation(user_id, request)


@router.get("/users/{user_id}/observations/{session_id}", response_model=ObservationSession)
def get_observation(
    user_id: str,
    session_id: str,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ObservationSession:
    session = service.get_observation(user_id, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Observation session not found")
    return session


@router.get("/users/{user_id}/agent-actions", response_model=AgentActionListResponse)
def list_agent_actions(
    user_id: str,
    session_id: str | None = Query(default=None, alias="sessionId"),
    limit: int = Query(default=100, ge=1, le=200),
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> AgentActionListResponse:
    return service.list_agent_actions(user_id, session_id=session_id, limit=limit)


@router.post("/users/{user_id}/external-imports", response_model=ExternalImportBatch)
def create_external_import(
    user_id: str,
    request: CreateExternalImportRequest,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ExternalImportBatch:
    return service.create_external_import(user_id, request)


@router.get("/users/{user_id}/external-imports", response_model=ExternalImportListResponse)
def list_external_imports(
    user_id: str,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ExternalImportListResponse:
    return service.list_external_imports(user_id)


@router.get("/users/{user_id}/external-imports/{batch_id}", response_model=ExternalImportBatch)
def get_external_import(
    user_id: str,
    batch_id: str,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ExternalImportBatch:
    batch = service.get_external_import(user_id, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="External import batch not found")
    return batch


@router.post("/users/{user_id}/external-imports/{batch_id}/confirm", response_model=ExternalImportBatch)
def confirm_external_import(
    user_id: str,
    batch_id: str,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ExternalImportBatch:
    batch = service.confirm_external_import(user_id, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="External import batch not found or not pending")
    return batch


@router.post("/users/{user_id}/external-imports/{batch_id}/reject", response_model=ExternalImportBatch)
def reject_external_import(
    user_id: str,
    batch_id: str,
    service: ObservationService = Depends(get_observation_service),
    _: str = Depends(require_user_scope),
) -> ExternalImportBatch:
    batch = service.reject_external_import(user_id, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="External import batch not found or not pending")
    return batch

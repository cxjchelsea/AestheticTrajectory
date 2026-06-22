from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import get_session_service
from app.core.config import settings
from app.schemas.session import SessionBootstrapResponse, SessionMeResponse
from app.services.session_service import SessionService

router = APIRouter(tags=["session"])


def _session_cookie_from_request(request: Request) -> str | None:
    return request.cookies.get(settings.session_cookie_name)


def _set_session_cookie(response: Response, session_token: str) -> None:
    max_age = settings.session_ttl_days * 24 * 60 * 60
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=max_age,
        path="/",
    )


@router.post("/session/bootstrap", response_model=SessionBootstrapResponse)
def bootstrap_session(
    request: Request,
    response: Response,
    service: SessionService = Depends(get_session_service),
) -> SessionBootstrapResponse:
    payload, created = service.bootstrap(_session_cookie_from_request(request))
    if payload.session_token and (
        created or payload.session_token != _session_cookie_from_request(request)
    ):
        _set_session_cookie(response, payload.session_token)
    return payload


@router.get("/session/me", response_model=SessionMeResponse)
def get_session_me(
    request: Request,
    service: SessionService = Depends(get_session_service),
) -> SessionMeResponse:
    return service.get_me(_session_cookie_from_request(request))

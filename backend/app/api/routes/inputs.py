from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_input_service
from app.core.auth import CurrentUser
from app.schemas.input import AestheticInputResponse, CreateInputRequest
from app.services.input_service import InputService

router = APIRouter(tags=["inputs"])


@router.post("/inputs", response_model=AestheticInputResponse)
def create_input(
    request: CreateInputRequest,
    service: InputService = Depends(get_input_service),
    current_user: CurrentUser = Depends(get_current_user),
) -> AestheticInputResponse:
    return service.create_input(request, current_user.user_id)

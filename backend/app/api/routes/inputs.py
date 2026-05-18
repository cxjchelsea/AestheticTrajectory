from fastapi import APIRouter, Depends

from app.api.deps import get_input_service
from app.schemas.input import AestheticInputResponse, CreateInputRequest
from app.services.input_service import InputService

router = APIRouter(tags=["inputs"])


@router.post("/inputs", response_model=AestheticInputResponse)
def create_input(
    request: CreateInputRequest,
    service: InputService = Depends(get_input_service),
) -> AestheticInputResponse:
    return service.create_input(request)

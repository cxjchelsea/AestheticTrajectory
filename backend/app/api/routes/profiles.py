from fastapi import APIRouter, Depends

from app.api.deps import get_profile_service, require_user_scope
from app.schemas.profile import ProfileResponse
from app.services.profile_service import ProfileService

router = APIRouter(tags=["profiles"])


@router.get("/users/{user_id}/profile", response_model=ProfileResponse)
def get_user_profile(
    user_id: str,
    service: ProfileService = Depends(get_profile_service),
    _: str = Depends(require_user_scope),
) -> ProfileResponse:
    return service.get_user_profile(user_id)

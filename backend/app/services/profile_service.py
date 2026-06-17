from app.schemas.profile import ProfileResponse


class ProfileService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def get_user_profile(self, user_id: str) -> ProfileResponse:
        return self.repository.get_or_build(user_id)

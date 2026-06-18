from app.schemas.profile import ProfileResponse
from app.services.temporal_profile_hints import apply_weakening_hints


class ProfileService:
    def __init__(self, repository, timeline_repository=None) -> None:
        self.repository = repository
        self.timeline_repository = timeline_repository

    def get_user_profile(self, user_id: str) -> ProfileResponse:
        profile = self.repository.get_or_build(user_id)
        if self.timeline_repository is None or profile.profile is None:
            return profile
        decline_labels = self.timeline_repository.list_decline_labels(user_id)
        return apply_weakening_hints(profile, decline_labels)

from app.repositories.memory_store import MemoryStore
from app.schemas.profile import ProfileResponse
from app.services.profile_builder import build_profile_from_sources


class ProfileRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def get_or_build(self, user_id: str) -> ProfileResponse:
        reports = [
            report
            for report_id, report in self.store.reports.items()
            if self.store.report_metadata.get(report_id, {}).get("user_id") == user_id
        ]
        feedback = [item for item in self.store.feedback.values() if item.user_id == user_id]
        profile = build_profile_from_sources(user_id, reports, feedback)
        self.store.profiles[user_id] = profile
        return profile

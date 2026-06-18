from app.schemas.profile import ProfileItem, ProfileResponse, UserProfile


def apply_weakening_hints(profile: ProfileResponse, decline_labels: set[str]) -> ProfileResponse:
    if profile.profile is None or not decline_labels:
        return profile

    updated_items: list[ProfileItem] = []
    for item in profile.profile.items:
        if item.status in {"rejected", "hidden", "deleted"}:
            updated_items.append(item)
            continue
        if _matches_decline(item.label, decline_labels) or _matches_decline(item.key, decline_labels):
            updated_items.append(item.model_copy(update={"status": "weakening"}))
        else:
            updated_items.append(item)

    return profile.model_copy(
        update={
            "profile": profile.profile.model_copy(update={"items": updated_items}),
        }
    )


def _matches_decline(value: str, decline_labels: set[str]) -> bool:
    normalized = value.strip().lower()
    for label in decline_labels:
        candidate = label.strip().lower()
        if candidate in normalized or normalized in candidate:
            return True
        if candidate.startswith("解释减弱：") and candidate.split("：", 1)[-1] in normalized:
            return True
    return False

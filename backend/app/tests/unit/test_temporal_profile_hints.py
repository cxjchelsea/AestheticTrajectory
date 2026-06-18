from app.schemas.profile import ProfileEvidence, ProfileItem, ProfileResponse, UserProfile
from app.schemas.common import utc_now
from app.services.temporal_profile_hints import apply_weakening_hints


def test_apply_weakening_hints_marks_matching_items() -> None:
    now = utc_now()
    profile = ProfileResponse(
        userId="user_a",
        profile=UserProfile(
            id="profile_user_a",
            summary="summary",
            version="v2-b",
            updatedAt=now,
            items=[
                ProfileItem(
                    id="item_001",
                    key="冷感空间",
                    label="冷感空间",
                    status="stable",
                    weight=0.6,
                    confidence=0.7,
                    sourceCount=2,
                    lastSeenAt=now,
                    evidence=[
                        ProfileEvidence(
                            id="evidence_001",
                            evidenceType="insight",
                            evidenceId="insight_001",
                            direction="positive",
                            weightDelta=0.4,
                            note="note",
                            createdAt=now,
                        )
                    ],
                )
            ],
        ),
    )

    updated = apply_weakening_hints(profile, {"解释减弱：冷感空间"})

    assert updated.profile is not None
    assert updated.profile.items[0].status == "weakening"

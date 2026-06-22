from dataclasses import dataclass

from fastapi import HTTPException


DEV_USER_ID = "user_anonymous"


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    auth_mode: str
    session_id: str | None = None
    session_present: bool = False

    def assert_scope(self, path_user_id: str) -> None:
        if self.auth_mode == "dev":
            return
        if path_user_id != self.user_id:
            raise HTTPException(status_code=403, detail="Access denied for requested user scope")

    def assert_resource_owner(self, owner_user_id: str | None) -> None:
        if self.auth_mode == "dev":
            return
        if owner_user_id is None or owner_user_id != self.user_id:
            raise HTTPException(status_code=403, detail="Access denied for requested resource")

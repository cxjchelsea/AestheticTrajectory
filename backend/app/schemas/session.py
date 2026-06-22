from pydantic import BaseModel, Field


class SessionBootstrapResponse(BaseModel):
    user_id: str = Field(alias="userId")
    session_token: str = Field(alias="sessionToken")
    auth_mode: str = Field(alias="authMode")

    model_config = {"populate_by_name": True}


class SessionMeResponse(BaseModel):
    user_id: str = Field(alias="userId")
    auth_mode: str = Field(alias="authMode")
    session_present: bool = Field(alias="sessionPresent")

    model_config = {"populate_by_name": True}

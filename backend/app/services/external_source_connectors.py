from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from app.schemas.common import utc_now
from app.schemas.external_context import ExternalContextItemDraft


@dataclass(frozen=True)
class OAuthTokenResult:
    access_token: str
    refresh_token: str | None
    scopes: list[str]
    expires_at: datetime | None
    resource_uri: str | None


class ExternalSourceConnector(Protocol):
    provider_name: str
    required_scopes: list[str]

    def build_authorization_url(
        self,
        *,
        user_id: str,
        state: str,
        code_challenge: str,
        redirect_uri: str,
    ) -> str:
        ...

    def exchange_code(
        self,
        *,
        code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> OAuthTokenResult:
        ...

    def list_items(self, *, access_token: str, limit: int) -> list[ExternalContextItemDraft]:
        ...


class MockOAuthExternalSourceConnector:
    provider_name = "demo_notes"
    required_scopes = ["read"]

    def build_authorization_url(
        self,
        *,
        user_id: str,
        state: str,
        code_challenge: str,
        redirect_uri: str,
    ) -> str:
        return (
            f"{redirect_uri}?code=mock_code_{user_id}&state={state}"
            f"&code_challenge={code_challenge}"
        )

    def exchange_code(
        self,
        *,
        code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> OAuthTokenResult:
        if not code.startswith("mock_code_"):
            raise ValueError("Mock OAuth code is invalid")
        return OAuthTokenResult(
            access_token=f"mock_access_{code_verifier[:12]}",
            refresh_token=f"mock_refresh_{code_verifier[-12:]}",
            scopes=self.required_scopes,
            expires_at=utc_now() + timedelta(hours=1),
            resource_uri=redirect_uri,
        )

    def list_items(self, *, access_token: str, limit: int) -> list[ExternalContextItemDraft]:
        if not access_token.startswith("mock_access_"):
            raise ValueError("External source access token is invalid")
        drafts = [
            ExternalContextItemDraft(
                title="外部笔记：低饱和与留白",
                snippet="收藏内容提到低饱和色彩、留白空间和安静观看节奏，只作为补充上下文。",
                sourceUri="mock://demo-notes/low-saturation",
                tags=["demo", "note", "read-only"],
            ),
            ExternalContextItemDraft(
                title="外部笔记：物体与空间距离",
                snippet="笔记记录了对物体、房间和远距离观察的兴趣，需经用户确认后才可引用。",
                sourceUri="mock://demo-notes/spatial-distance",
                tags=["demo", "note", "supplementary"],
            ),
            ExternalContextItemDraft(
                title="外部收藏：柔和叙事片段",
                snippet="收藏片段描述柔和过渡、低刺激叙事和非人物中心的画面组织。",
                sourceUri="mock://demo-notes/soft-narrative",
                tags=["demo", "bookmark", "read-only"],
            ),
        ]
        return drafts[:limit]


def get_external_source_connector(runtime: str, provider: str) -> ExternalSourceConnector:
    if runtime == "mock_oauth":
        return MockOAuthExternalSourceConnector()
    if runtime == "mcp_oauth":
        raise ValueError("EXTERNAL_SOURCE_RUNTIME=mcp_oauth is reserved; V5-C starts with mock_oauth.")
    raise ValueError("External source runtime is disabled")

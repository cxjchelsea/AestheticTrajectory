"""add user_sessions table and backfill user_anonymous

Revision ID: 20260617_0006
Revises: 20260618_0005
Create Date: 2026-06-17
"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260617_0006"
down_revision: Union[str, None] = "20260618_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_sessions_user_id", "user_sessions", ["user_id"])

    now = datetime.now(timezone.utc)
    op.execute(
        sa.text(
            """
            INSERT INTO users (id, anonymous_id, created_at, updated_at)
            VALUES ('user_anonymous', 'user_anonymous', :now, :now)
            ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(now=now)
    )


def downgrade() -> None:
    op.drop_index("ix_user_sessions_user_id", table_name="user_sessions")
    op.drop_table("user_sessions")

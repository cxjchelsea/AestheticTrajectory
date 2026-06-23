"""add external source oauth connection tables

Revision ID: 20260622_0007
Revises: 20260617_0006
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260622_0007"
down_revision: Union[str, None] = "20260617_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_source_connections",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("scopes_json", sa.JSON(), nullable=False),
        sa.Column("access_token_ciphertext", sa.Text(), nullable=True),
        sa.Column("refresh_token_ciphertext", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resource_uri", sa.Text(), nullable=True),
        sa.Column("last_connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_external_source_connections_user_id", "external_source_connections", ["user_id"])
    op.create_index("ix_external_source_connections_provider", "external_source_connections", ["provider"])
    op.create_index("ix_external_source_connections_status", "external_source_connections", ["status"])
    op.create_index(
        "ux_external_source_connections_user_provider",
        "external_source_connections",
        ["user_id", "provider"],
        unique=True,
    )

    op.create_table(
        "external_oauth_states",
        sa.Column("state", sa.String(length=128), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("code_verifier", sa.Text(), nullable=False),
        sa.Column("redirect_after", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_external_oauth_states_user_id", "external_oauth_states", ["user_id"])
    op.create_index("ix_external_oauth_states_provider", "external_oauth_states", ["provider"])
    op.create_index("ix_external_oauth_states_expires_at", "external_oauth_states", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_external_oauth_states_expires_at", table_name="external_oauth_states")
    op.drop_index("ix_external_oauth_states_provider", table_name="external_oauth_states")
    op.drop_index("ix_external_oauth_states_user_id", table_name="external_oauth_states")
    op.drop_table("external_oauth_states")

    op.drop_index("ux_external_source_connections_user_provider", table_name="external_source_connections")
    op.drop_index("ix_external_source_connections_status", table_name="external_source_connections")
    op.drop_index("ix_external_source_connections_provider", table_name="external_source_connections")
    op.drop_index("ix_external_source_connections_user_id", table_name="external_source_connections")
    op.drop_table("external_source_connections")

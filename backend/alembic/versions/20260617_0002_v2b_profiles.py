"""add v2b profile evidence tables

Revision ID: 20260617_0002
Revises: 20260616_0001
Create Date: 2026-06-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260617_0002"
down_revision: Union[str, None] = "20260616_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])

    op.create_table(
        "profile_items",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("profile_id", sa.String(length=64), sa.ForeignKey("user_profiles.id"), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("source_count", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_profile_items_profile_id", "profile_items", ["profile_id"])
    op.create_index("ix_profile_items_key", "profile_items", ["key"])
    op.create_index("ix_profile_items_status", "profile_items", ["status"])

    op.create_table(
        "profile_evidence",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("profile_item_id", sa.String(length=64), sa.ForeignKey("profile_items.id"), nullable=False),
        sa.Column("evidence_type", sa.String(length=32), nullable=False),
        sa.Column("evidence_id", sa.String(length=64), nullable=False),
        sa.Column("direction", sa.String(length=32), nullable=False),
        sa.Column("weight_delta", sa.Float(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_profile_evidence_profile_item_id", "profile_evidence", ["profile_item_id"])
    op.create_index("ix_profile_evidence_evidence_type", "profile_evidence", ["evidence_type"])
    op.create_index("ix_profile_evidence_evidence_id", "profile_evidence", ["evidence_id"])
    op.create_index("ix_profile_evidence_direction", "profile_evidence", ["direction"])


def downgrade() -> None:
    op.drop_table("profile_evidence")
    op.drop_table("profile_items")
    op.drop_table("user_profiles")

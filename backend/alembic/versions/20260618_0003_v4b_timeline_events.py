"""add aesthetic timeline events table

Revision ID: 20260618_0003
Revises: 20260617_0002
Create Date: 2026-06-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0003"
down_revision: Union[str, None] = "20260617_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aesthetic_timeline_events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("related_report_ids_json", sa.JSON(), nullable=False),
        sa.Column("related_insight_ids_json", sa.JSON(), nullable=False),
        sa.Column("related_feedback_ids_json", sa.JSON(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("dedupe_key", sa.String(length=256), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_aesthetic_timeline_events_user_id", "aesthetic_timeline_events", ["user_id"])
    op.create_index("ix_aesthetic_timeline_events_event_type", "aesthetic_timeline_events", ["event_type"])
    op.create_index("ix_aesthetic_timeline_events_dedupe_key", "aesthetic_timeline_events", ["dedupe_key"])
    op.create_index("ix_aesthetic_timeline_events_occurred_at", "aesthetic_timeline_events", ["occurred_at"])
    op.create_index(
        "uq_aesthetic_timeline_events_user_dedupe",
        "aesthetic_timeline_events",
        ["user_id", "dedupe_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_aesthetic_timeline_events_user_dedupe", table_name="aesthetic_timeline_events")
    op.drop_table("aesthetic_timeline_events")

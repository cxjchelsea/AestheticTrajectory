"""initial v1 persistence schema

Revision ID: 20260616_0001
Revises:
Create Date: 2026-06-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260616_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def json_type():
    return postgresql.JSONB().with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("anonymous_id", sa.String(length=128), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "aesthetic_inputs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("content_text", sa.Text()),
        sa.Column("file_url", sa.Text()),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_aesthetic_inputs_user_id", "aesthetic_inputs", ["user_id"])
    op.create_table(
        "input_features",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("input_id", sa.String(length=64), nullable=False),
        sa.Column("feature_type", sa.String(length=16), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=128), nullable=False),
        sa.Column("feature_json", json_type(), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_input_features_input_id", "input_features", ["input_id"])
    op.create_table(
        "embedding_records",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("owner_type", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.String(length=64), nullable=False),
        sa.Column("collection_name", sa.String(length=128), nullable=False),
        sa.Column("chroma_id", sa.String(length=128), nullable=False),
        sa.Column("model_name", sa.String(length=128), nullable=False),
        sa.Column("vector_dimension", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_embedding_records_owner_type", "embedding_records", ["owner_type"])
    op.create_index("ix_embedding_records_owner_id", "embedding_records", ["owner_id"])
    op.create_table(
        "analysis_jobs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("report_id", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_analysis_jobs_user_id", "analysis_jobs", ["user_id"])
    op.create_index("ix_analysis_jobs_status", "analysis_jobs", ["status"])
    op.create_index("ix_analysis_jobs_report_id", "analysis_jobs", ["report_id"])
    op.create_table(
        "aesthetic_reports",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64)),
        sa.Column("job_id", sa.String(length=64)),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("low_level_features_json", json_type(), nullable=False),
        sa.Column("similarity_groups_json", json_type(), nullable=False),
        sa.Column("interpretations_json", json_type(), nullable=False),
        sa.Column("report_json", json_type(), nullable=False),
        sa.Column("markdown", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_aesthetic_reports_user_id", "aesthetic_reports", ["user_id"])
    op.create_index("ix_aesthetic_reports_job_id", "aesthetic_reports", ["job_id"])
    op.create_table(
        "possible_interpretations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("report_id", sa.String(length=64), sa.ForeignKey("aesthetic_reports.id"), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.String(length=64)),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_json", json_type(), nullable=False),
        sa.Column("alternative_names_json", json_type()),
        sa.Column("uncertainty", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_possible_interpretations_report_id", "possible_interpretations", ["report_id"])
    op.create_table(
        "insights",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("report_id", sa.String(length=64), sa.ForeignKey("aesthetic_reports.id"), nullable=False),
        sa.Column("interpretation_id", sa.String(length=64)),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("observation", sa.Text(), nullable=False),
        sa.Column("evidence_json", json_type(), nullable=False),
        sa.Column("interpretation", sa.Text(), nullable=False),
        sa.Column("uncertainty", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_insights_report_id", "insights", ["report_id"])
    op.create_index("ix_insights_interpretation_id", "insights", ["interpretation_id"])
    op.create_table(
        "insight_feedback",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("insight_id", sa.String(length=64), nullable=False),
        sa.Column("interpretation_id", sa.String(length=64)),
        sa.Column("rating", sa.String(length=32), nullable=False),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_insight_feedback_user_id", "insight_feedback", ["user_id"])
    op.create_index("ix_insight_feedback_insight_id", "insight_feedback", ["insight_id"])
    op.create_index("ix_insight_feedback_interpretation_id", "insight_feedback", ["interpretation_id"])
    op.create_table(
        "analysis_logs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("job_id", sa.String(length=64), nullable=False),
        sa.Column("step_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("model_name", sa.String(length=128)),
        sa.Column("prompt_version", sa.String(length=128)),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("error_type", sa.String(length=128)),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_analysis_logs_job_id", "analysis_logs", ["job_id"])
    op.create_index("ix_analysis_logs_step_id", "analysis_logs", ["step_id"])
    op.create_index("ix_analysis_logs_status", "analysis_logs", ["status"])


def downgrade() -> None:
    op.drop_table("analysis_logs")
    op.drop_table("insight_feedback")
    op.drop_table("insights")
    op.drop_table("possible_interpretations")
    op.drop_table("aesthetic_reports")
    op.drop_table("analysis_jobs")
    op.drop_table("embedding_records")
    op.drop_table("input_features")
    op.drop_table("aesthetic_inputs")
    op.drop_table("users")

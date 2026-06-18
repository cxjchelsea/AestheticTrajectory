"""add aesthetic knowledge graph tables

Revision ID: 20260618_0004
Revises: 20260618_0003
Create Date: 2026-06-18
"""

from datetime import datetime, timezone
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260618_0004"
down_revision: Union[str, None] = "20260618_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "aesthetic_concepts",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("feature_tags_json", sa.JSON(), nullable=False),
        sa.Column("source_refs_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_aesthetic_concepts_slug", "aesthetic_concepts", ["slug"], unique=True)

    op.create_table(
        "aesthetic_concept_relations",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("from_concept_id", sa.String(length=64), nullable=False),
        sa.Column("to_concept_id", sa.String(length=64), nullable=False),
        sa.Column("predicate", sa.String(length=32), nullable=False),
        sa.Column("source_evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_aesthetic_concept_relations_from", "aesthetic_concept_relations", ["from_concept_id"])
    op.create_index("ix_aesthetic_concept_relations_to", "aesthetic_concept_relations", ["to_concept_id"])
    op.create_index("ix_aesthetic_concept_relations_predicate", "aesthetic_concept_relations", ["predicate"])

    concepts = sa.table(
        "aesthetic_concepts",
        sa.column("id", sa.String),
        sa.column("slug", sa.String),
        sa.column("label", sa.Text),
        sa.column("description", sa.Text),
        sa.column("feature_tags_json", sa.JSON),
        sa.column("source_refs_json", sa.JSON),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    relations = sa.table(
        "aesthetic_concept_relations",
        sa.column("id", sa.String),
        sa.column("from_concept_id", sa.String),
        sa.column("to_concept_id", sa.String),
        sa.column("predicate", sa.String),
        sa.column("source_evidence_json", sa.JSON),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        concepts,
        [
            {
                "id": "concept_low_saturation",
                "slug": "low-saturation",
                "label": "低饱和结构",
                "description": "以低饱和色块和弱对比为主的视觉结构气质。",
                "feature_tags_json": ["saturation=low", "density=low"],
                "source_refs_json": ["kb_low_saturation_space"],
                "created_at": now,
            },
            {
                "id": "concept_medium_low_saturation",
                "slug": "medium-low-saturation",
                "label": "中低饱和过渡",
                "description": "中低饱和常用于描述柔和过渡与弱对比场景。",
                "feature_tags_json": ["saturation=medium-low"],
                "source_refs_json": ["kb_medium_low_saturation"],
                "created_at": now,
            },
            {
                "id": "concept_person_absent",
                "slug": "person-absent-composition",
                "label": "非人物中心构图",
                "description": "更偏空间、物体或片段意象而非明确人物行动。",
                "feature_tags_json": ["presence=person_absent"],
                "source_refs_json": ["kb_person_absent_composition"],
                "created_at": now,
            },
            {
                "id": "concept_low_density",
                "slug": "low-density-fragment",
                "label": "低密度片段观察",
                "description": "元素较少、留白明显的片段式观察结构。",
                "feature_tags_json": ["density=low", "presence=person_absent"],
                "source_refs_json": ["kb_low_density_fragment"],
                "created_at": now,
            },
        ],
    )
    op.bulk_insert(
        relations,
        [
            {
                "id": "rel_low_saturation_low_density",
                "from_concept_id": "concept_low_saturation",
                "to_concept_id": "concept_low_density",
                "predicate": "related_to",
                "source_evidence_json": {
                    "docIds": ["kb_low_saturation_space", "kb_low_density_fragment"],
                    "note": "curated from project knowledge v1",
                },
                "created_at": now,
            },
            {
                "id": "rel_low_saturation_medium_low",
                "from_concept_id": "concept_low_saturation",
                "to_concept_id": "concept_medium_low_saturation",
                "predicate": "contrasts_with",
                "source_evidence_json": {
                    "docIds": ["kb_low_saturation_space", "kb_medium_low_saturation"],
                    "note": "curated contrast pair from project knowledge v1",
                },
                "created_at": now,
            },
            {
                "id": "rel_person_absent_low_density",
                "from_concept_id": "concept_person_absent",
                "to_concept_id": "concept_low_density",
                "predicate": "example_of",
                "source_evidence_json": {
                    "docIds": ["kb_person_absent_composition", "kb_low_density_fragment"],
                    "note": "curated example relation from project knowledge v1",
                },
                "created_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("aesthetic_concept_relations")
    op.drop_table("aesthetic_concepts")

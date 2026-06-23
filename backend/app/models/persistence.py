from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


def json_column(nullable: bool = False):
    return mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=nullable)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    anonymous_id: Mapped[str | None] = mapped_column(String(128), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserSessionModel(Base):
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AestheticInputModel(Base):
    __tablename__ = "aesthetic_inputs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    type: Mapped[str] = mapped_column(String(16))
    content_text: Mapped[str | None] = mapped_column(Text)
    file_url: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(64))
    title: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class InputFeatureModel(Base):
    __tablename__ = "input_features"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    input_id: Mapped[str] = mapped_column(String(64), index=True)
    feature_type: Mapped[str] = mapped_column(String(16))
    model_name: Mapped[str] = mapped_column(String(128))
    prompt_version: Mapped[str] = mapped_column(String(128))
    feature_json: Mapped[dict] = json_column()
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class EmbeddingRecordModel(Base):
    __tablename__ = "embedding_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    owner_type: Mapped[str] = mapped_column(String(32), index=True)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    collection_name: Mapped[str] = mapped_column(String(128))
    chroma_id: Mapped[str] = mapped_column(String(128))
    model_name: Mapped[str] = mapped_column(String(128))
    vector_dimension: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AnalysisJobModel(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    input_count: Mapped[int] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    report_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AestheticReportModel(Base):
    __tablename__ = "aesthetic_reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    job_id: Mapped[str | None] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
    low_level_features_json: Mapped[list] = json_column()
    similarity_groups_json: Mapped[list] = json_column()
    interpretations_json: Mapped[list] = json_column()
    report_json: Mapped[dict] = json_column()
    markdown: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PossibleInterpretationModel(Base):
    __tablename__ = "possible_interpretations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    report_id: Mapped[str] = mapped_column(String(64), ForeignKey("aesthetic_reports.id"), index=True)
    target_type: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str | None] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    evidence_json: Mapped[list] = json_column()
    alternative_names_json: Mapped[list | None] = json_column(nullable=True)
    uncertainty: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InsightModel(Base):
    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    report_id: Mapped[str] = mapped_column(String(64), ForeignKey("aesthetic_reports.id"), index=True)
    interpretation_id: Mapped[str | None] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text)
    observation: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[list] = json_column()
    interpretation: Mapped[str] = mapped_column(Text)
    uncertainty: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class InsightFeedbackModel(Base):
    __tablename__ = "insight_feedback"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    insight_id: Mapped[str] = mapped_column(String(64), index=True)
    interpretation_id: Mapped[str | None] = mapped_column(String(64), index=True)
    rating: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    summary: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProfileItemModel(Base):
    __tablename__ = "profile_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    profile_id: Mapped[str] = mapped_column(String(64), ForeignKey("user_profiles.id"), index=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    label: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), index=True)
    weight: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    source_count: Mapped[int] = mapped_column(Integer)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProfileEvidenceModel(Base):
    __tablename__ = "profile_evidence"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    profile_item_id: Mapped[str] = mapped_column(String(64), ForeignKey("profile_items.id"), index=True)
    evidence_type: Mapped[str] = mapped_column(String(32), index=True)
    evidence_id: Mapped[str] = mapped_column(String(64), index=True)
    direction: Mapped[str] = mapped_column(String(32), index=True)
    weight_delta: Mapped[float] = mapped_column(Float)
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AnalysisLogModel(Base):
    __tablename__ = "analysis_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), index=True)
    step_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    model_name: Mapped[str | None] = mapped_column(String(128))
    prompt_version: Mapped[str | None] = mapped_column(String(128))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_type: Mapped[str | None] = mapped_column(String(128))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AestheticTimelineEventModel(Base):
    __tablename__ = "aesthetic_timeline_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    related_report_ids_json: Mapped[list] = json_column()
    related_insight_ids_json: Mapped[list] = json_column()
    related_feedback_ids_json: Mapped[list] = json_column()
    evidence_json: Mapped[dict] = json_column()
    dedupe_key: Mapped[str] = mapped_column(String(256), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AestheticConceptModel(Base):
    __tablename__ = "aesthetic_concepts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    label: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    feature_tags_json: Mapped[list] = json_column()
    source_refs_json: Mapped[list] = json_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AestheticConceptRelationModel(Base):
    __tablename__ = "aesthetic_concept_relations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    from_concept_id: Mapped[str] = mapped_column(String(64), index=True)
    to_concept_id: Mapped[str] = mapped_column(String(64), index=True)
    predicate: Mapped[str] = mapped_column(String(32), index=True)
    source_evidence_json: Mapped[dict] = json_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ObservationSessionModel(Base):
    __tablename__ = "observation_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    trigger_source: Mapped[str] = mapped_column(String(64))
    period: Mapped[str | None] = mapped_column(String(16))
    summary: Mapped[str | None] = mapped_column(Text)
    questions_json: Mapped[list] = json_column()
    evidence_refs_json: Mapped[list] = json_column()
    message: Mapped[str | None] = mapped_column(Text)
    disclaimer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AgentActionLogModel(Base):
    __tablename__ = "agent_action_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    step_index: Mapped[int] = mapped_column(Integer)
    tool_name: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str] = mapped_column(Text)
    input_refs_json: Mapped[list] = json_column()
    output_refs_json: Mapped[list] = json_column()
    status: Mapped[str] = mapped_column(String(32))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExternalImportBatchModel(Base):
    __tablename__ = "external_import_batches"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    source_system: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), index=True)
    item_count: Mapped[int] = mapped_column(Integer)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExternalContextItemModel(Base):
    __tablename__ = "external_context_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text)
    snippet: Mapped[str] = mapped_column(Text)
    source_uri: Mapped[str | None] = mapped_column(Text)
    tags_json: Mapped[list] = json_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExternalSourceConnectionModel(Base):
    __tablename__ = "external_source_connections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    scopes_json: Mapped[list] = json_column()
    access_token_ciphertext: Mapped[str | None] = mapped_column(Text)
    refresh_token_ciphertext: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resource_uri: Mapped[str | None] = mapped_column(Text)
    last_connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExternalOAuthStateModel(Base):
    __tablename__ = "external_oauth_states"

    state: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    code_verifier: Mapped[str] = mapped_column(Text)
    redirect_after: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

from dataclasses import dataclass, field

from app.schemas.analysis_log import AnalysisLogRecord
from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.embedding import EmbeddingRecord
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse
from app.schemas.profile import ProfileResponse
from app.schemas.report import ReportResponse
from app.schemas.agent import AgentActionLog, ObservationSession
from app.schemas.external_context import ExternalContextItem, ExternalImportBatch
from app.schemas.external_source import ExternalOAuthState
from app.schemas.timeline import TimelineEvent


@dataclass
class MemoryStore:
    inputs: dict[str, AestheticInputResponse] = field(default_factory=dict)
    features: dict[str, InputFeature] = field(default_factory=dict)
    embedding_records: dict[str, EmbeddingRecord] = field(default_factory=dict)
    jobs: dict[str, AnalysisJobResponse] = field(default_factory=dict)
    reports: dict[str, ReportResponse] = field(default_factory=dict)
    report_metadata: dict[str, dict[str, object]] = field(default_factory=dict)
    feedback: dict[str, InsightFeedbackResponse] = field(default_factory=dict)
    analysis_logs: dict[str, AnalysisLogRecord] = field(default_factory=dict)
    profiles: dict[str, ProfileResponse] = field(default_factory=dict)
    timeline_events: dict[str, TimelineEvent] = field(default_factory=dict)
    timeline_dedupe_keys: set[tuple[str, str]] = field(default_factory=set)
    observation_sessions: dict[str, ObservationSession] = field(default_factory=dict)
    agent_action_logs: dict[str, AgentActionLog] = field(default_factory=dict)
    external_import_batches: dict[str, ExternalImportBatch] = field(default_factory=dict)
    external_context_items: dict[str, ExternalContextItem] = field(default_factory=dict)
    external_source_connections: dict[str, dict[str, object]] = field(default_factory=dict)
    external_oauth_states: dict[str, ExternalOAuthState] = field(default_factory=dict)
    user_sessions: dict[str, dict[str, object]] = field(default_factory=dict)


store = MemoryStore()

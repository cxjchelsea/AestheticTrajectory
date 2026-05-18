from dataclasses import dataclass, field

from app.schemas.analysis_job import AnalysisJobResponse
from app.schemas.embedding import EmbeddingRecord
from app.schemas.feedback import InsightFeedbackResponse
from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse
from app.schemas.report import ReportResponse


@dataclass
class MemoryStore:
    inputs: dict[str, AestheticInputResponse] = field(default_factory=dict)
    features: dict[str, InputFeature] = field(default_factory=dict)
    embedding_records: dict[str, EmbeddingRecord] = field(default_factory=dict)
    jobs: dict[str, AnalysisJobResponse] = field(default_factory=dict)
    reports: dict[str, ReportResponse] = field(default_factory=dict)
    feedback: dict[str, InsightFeedbackResponse] = field(default_factory=dict)


store = MemoryStore()

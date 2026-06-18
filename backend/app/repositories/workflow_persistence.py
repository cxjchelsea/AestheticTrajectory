from dataclasses import dataclass

from app.vector_store.input_vector_store import ChromaWriteResult


@dataclass
class WorkflowPersistence:
    feature_repository: object
    embedding_record_repository: object
    report_repository: object
    analysis_log_repository: object
    feedback_repository: object
    timeline_repository: object | None = None
    chroma_write_results: dict[str, ChromaWriteResult] | None = None

    def save_chroma_write_result(self, job_id: str, result: ChromaWriteResult) -> None:
        if self.chroma_write_results is not None:
            self.chroma_write_results[job_id] = result

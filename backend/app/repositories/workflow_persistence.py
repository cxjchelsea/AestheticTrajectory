from dataclasses import dataclass


@dataclass
class WorkflowPersistence:
    feature_repository: object
    embedding_record_repository: object
    report_repository: object
    analysis_log_repository: object

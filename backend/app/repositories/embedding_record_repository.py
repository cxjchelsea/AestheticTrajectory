from app.repositories.memory_store import MemoryStore
from app.schemas.embedding import EmbeddingRecord


class EmbeddingRecordRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save_many(self, records: list[EmbeddingRecord]) -> list[EmbeddingRecord]:
        for record in records:
            self.store.embedding_records[record.id] = record
        return records

from app.repositories.memory_store import MemoryStore
from app.schemas.input import AestheticInputResponse


class InputRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save(self, input_record: AestheticInputResponse) -> AestheticInputResponse:
        self.store.inputs[input_record.id] = input_record
        return input_record

    def get_many(self, input_ids: list[str]) -> list[AestheticInputResponse]:
        return [self.store.inputs[input_id] for input_id in input_ids if input_id in self.store.inputs]

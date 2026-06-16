from app.repositories.memory_store import MemoryStore
from app.schemas.feature import InputFeature


class FeatureRepository:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def save_many(self, features: list[InputFeature]) -> list[InputFeature]:
        for feature in features:
            self.store.features[feature.input_id] = feature
        return features

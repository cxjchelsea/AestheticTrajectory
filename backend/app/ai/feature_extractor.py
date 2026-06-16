from typing import Protocol

from app.schemas.feature import InputFeature
from app.schemas.input import AestheticInputResponse


class FeatureExtractor(Protocol):
    model_name: str

    def extract(self, input_record: AestheticInputResponse, index: int) -> InputFeature:
        """Return a validated low-level aesthetic feature record for one input."""
        ...

from typing import TypeVar

from pydantic import BaseModel

from app.schemas.feature import InputFeature


SchemaT = TypeVar("SchemaT", bound=BaseModel)


def validate_structured_output(schema: type[SchemaT], payload: object) -> SchemaT:
    return schema.model_validate(payload)


def validate_input_feature(feature: InputFeature) -> InputFeature:
    if not feature.prompt_version:
        raise ValueError("InputFeature must include promptVersion")
    if not feature.model_name:
        raise ValueError("InputFeature must include modelName")
    if not feature.low_level_features:
        raise ValueError("InputFeature must include lowLevelFeatures")
    if not feature.sample_evidence:
        raise ValueError("InputFeature must include sampleEvidence")

    for name, signal in feature.low_level_features.items():
        if not signal.evidence:
            raise ValueError(f"Feature signal '{name}' must include evidence")

    return feature

from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.input import InputType


FeatureValue = Literal["low", "medium-low", "medium", "high", "person_absent"]


class FeatureSignal(BaseModel):
    value: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]


class InputFeature(BaseModel):
    input_id: str = Field(alias="inputId")
    feature_type: InputType = Field(alias="featureType")
    low_level_features: dict[str, FeatureSignal] = Field(alias="lowLevelFeatures")
    sample_evidence: list[str] = Field(alias="sampleEvidence")
    prompt_version: str = Field(alias="promptVersion")

    model_config = {"populate_by_name": True}

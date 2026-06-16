from pydantic import BaseModel, Field

from app.schemas.input import InputType


class FeatureSignal(BaseModel):
    value: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(min_length=1)


class InputFeature(BaseModel):
    input_id: str = Field(alias="inputId")
    feature_type: InputType = Field(alias="featureType")
    low_level_features: dict[str, FeatureSignal] = Field(alias="lowLevelFeatures", min_length=1)
    sample_evidence: list[str] = Field(alias="sampleEvidence", min_length=1)
    prompt_version: str = Field(alias="promptVersion")
    model_name: str = Field(alias="modelName")

    model_config = {"populate_by_name": True}

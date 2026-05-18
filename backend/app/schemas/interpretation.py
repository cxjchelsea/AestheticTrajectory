from pydantic import BaseModel, Field


class SimilarityGroup(BaseModel):
    group_id: str = Field(alias="groupId")
    name: str
    input_ids: list[str] = Field(alias="inputIds")
    common_features: list[str] = Field(alias="commonFeatures")
    uncertainty: str

    model_config = {"populate_by_name": True}


class PossibleInterpretation(BaseModel):
    id: str
    name: str
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(alias="evidenceRefs")
    uncertainty: str

    model_config = {"populate_by_name": True}

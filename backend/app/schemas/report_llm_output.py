from pydantic import BaseModel, Field


class InterpretationLLMItem(BaseModel):
    id: str
    name: str
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(alias="evidenceRefs", min_length=1)
    uncertainty: str

    model_config = {"populate_by_name": True}


class InsightLLMItem(BaseModel):
    insight_id: str = Field(alias="insightId")
    title: str
    observation: str
    interpretation: str
    evidence_refs: list[str] = Field(alias="evidenceRefs", min_length=1)
    uncertainty: str
    confidence: float = Field(ge=0, le=1)

    model_config = {"populate_by_name": True}


class InterpretationLLMOutput(BaseModel):
    prompt_version: str = Field(alias="promptVersion")
    model_name: str = Field(alias="modelName")
    interpretations: list[InterpretationLLMItem] = Field(min_length=1)
    insights: list[InsightLLMItem] = Field(min_length=1)
    rejected_claims: list[dict[str, str]] = Field(default_factory=list, alias="rejectedClaims")

    model_config = {"populate_by_name": True}

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.threat import ThreatActorCategory


class ThreatActorCreate(BaseModel):
    name: str
    category: ThreatActorCategory
    motivation: str
    sophistication: str = "Medium"
    description: str = ""


class ThreatActorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: ThreatActorCategory
    motivation: str
    sophistication: str
    description: str


class ThreatCreate(BaseModel):
    name: str
    description: str
    threat_actor_id: int | None = None
    mitre_technique_id: str | None = None
    mitre_technique_name: str | None = None
    why_relevant: str

    @field_validator("why_relevant")
    @classmethod
    def why_relevant_must_be_specific(cls, value: str) -> str:
        if len(value.strip()) < 20:
            raise ValueError(
                "why_relevant must explain why this threat matters for THIS environment "
                "(at least 20 characters) - a MITRE ID alone is not a threat model."
            )
        return value


class ThreatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    threat_actor_id: int | None
    mitre_technique_id: str | None
    mitre_technique_name: str | None
    why_relevant: str


class AttackPathStepCreate(BaseModel):
    sequence: int
    description: str
    asset_id: int | None = None
    threat_id: int | None = None


class AttackPathStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sequence: int
    description: str
    asset_id: int | None
    threat_id: int | None


class AttackPathCreate(BaseModel):
    name: str
    description: str
    entry_point: str
    target_asset_id: int
    likelihood: int
    impact: int
    notes: str = ""
    steps: list[AttackPathStepCreate] = []

    @field_validator("likelihood", "impact")
    @classmethod
    def one_to_five(cls, value: int) -> int:
        if not 1 <= value <= 5:
            raise ValueError("must be between 1 and 5")
        return value


class AttackPathRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    entry_point: str
    target_asset_id: int
    likelihood: int
    impact: int
    score: int
    notes: str
    steps: list[AttackPathStepRead]

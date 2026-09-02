from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.incident import IncidentSeverity, IncidentStage


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: IncidentSeverity
    affected_asset_ids: list[int] = []
    indicators: list[str] = []
    recommended_containment: str = ""


class IncidentAdvanceRequest(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def must_be_substantive(cls, value: str) -> str:
        if len(value.strip()) < 10:
            raise ValueError("Provide a substantive note (at least 10 characters) for the timeline.")
        return value


class IncidentUpdate(BaseModel):
    remediation: str | None = None
    lessons_learned: str | None = None
    recommended_containment: str | None = None


class IncidentTimelineEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stage: IncidentStage
    description: str
    occurred_at: datetime


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    severity: IncidentSeverity
    stage: IncidentStage
    affected_asset_ids: list[int]
    indicators: list[str]
    recommended_containment: str
    remediation: str
    lessons_learned: str
    detected_at: datetime
    timeline: list[IncidentTimelineEntryRead]

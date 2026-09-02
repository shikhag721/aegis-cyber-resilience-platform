from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.models.monitoring import SecurityEventType


class SecurityEventCreate(BaseModel):
    event_type: SecurityEventType
    username: str
    asset_id: int | None = None
    source_ip: str = ""
    source_location: str = ""
    details: str = ""
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: SecurityEventType
    username: str
    asset_id: int | None
    source_ip: str
    source_location: str
    details: str
    occurred_at: datetime


class CorrelationFindingRead(BaseModel):
    username: str
    severity: str
    matched_event_types: list[str]
    narrative: str

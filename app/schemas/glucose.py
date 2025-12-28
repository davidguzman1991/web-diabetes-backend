from datetime import date, datetime
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class GlucoseLogCreate(BaseModel):
    patient_id: UUID | None = None
    date: date | None = None
    value: int = Field(ge=20, le=600)
    measurement_type: Literal["fasting", "postprandial"] | None = None
    type: Literal["ayuno", "postprandial"] | None = None
    taken_at: datetime | None = None
    observation: str | None = None


class GlucoseLogOut(BaseModel):
    id: UUID
    patient_id: UUID
    value: int
    type: str
    taken_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

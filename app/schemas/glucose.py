from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class GlucoseLogCreate(BaseModel):
    patient_id: Optional[UUID] = None
    date: Optional[date] = None
    value: int = Field(ge=20, le=600)
    measurement_type: Optional[Literal["fasting", "postprandial"]] = None
    type: Optional[Literal["ayuno", "postprandial"]] = None
    taken_at: Optional[datetime] = None
    observation: Optional[str] = None


class GlucoseLogOut(BaseModel):
    id: UUID
    patient_id: UUID
    value: int
    type: str
    taken_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PatientTaskOut(BaseModel):
    id: UUID
    patient_id: UUID
    title: str
    description: str | None = None
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

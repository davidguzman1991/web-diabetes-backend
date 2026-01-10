from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


class AdminConsultationListItem(BaseModel):
    consultation_id: str
    created_at: datetime
    consultation_date: date | None = None
    patient_username: str | None = None
    patient_name: str | None = None
    patient_cedula: str | None = None
    diagnosis: str | None = None
    note_preview: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminConsultationListResponse(BaseModel):
    items: list[AdminConsultationListItem]

    model_config = ConfigDict(from_attributes=True)


class AdminMedicationTopItem(BaseModel):
    nombre: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class AdminMedicationTopResponse(BaseModel):
    from_date: date = Field(alias="from")
    to_date: date = Field(alias="to")
    limit: int
    items: list[AdminMedicationTopItem]

    model_config = ConfigDict(populate_by_name=True)

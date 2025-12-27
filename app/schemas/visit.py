from datetime import date, datetime
from pydantic import BaseModel

from app.schemas.prescription import PrescriptionItemCreate, PrescriptionItemOut


class VisitBase(BaseModel):
    fecha_consulta: date
    diagnostico: str
    notas_medico: str | None = None


class VisitCreate(VisitBase):
    items: list[PrescriptionItemCreate]


class VisitOut(VisitBase):
    id: str
    patient_id: str
    created_at: datetime
    updated_at: datetime
    items: list[PrescriptionItemOut]

    model_config = {"from_attributes": True}

    class Config:
        from_attributes = True


class VisitListItem(BaseModel):
    id: str
    fecha_consulta: date
    diagnostico: str

    model_config = {"from_attributes": True}

    class Config:
        from_attributes = True

from datetime import datetime
from pydantic import BaseModel


class MedicationIn(BaseModel):
    nombre: str
    dosis: str
    horario: str
    via: str
    duracion: str
    notas: str | None = None


class MedicationOut(MedicationIn):
    id: str

    model_config = {"from_attributes": True}

    class Config:
        from_attributes = True


class ConsultaBase(BaseModel):
    diagnostico: str | None = None
    notas_medicas: str | None = None
    indicaciones_generales: str | None = None


class ConsultaCreate(ConsultaBase):
    medicamentos: list[MedicationIn]


class ConsultaOut(ConsultaBase):
    id: str
    patient_user_id: str
    created_by_admin_id: str
    fecha: datetime
    medicamentos: list[MedicationOut]

    model_config = {"from_attributes": True}

    class Config:
        from_attributes = True


class ConsultaSummary(BaseModel):
    id: str
    fecha: datetime
    diagnostico: str | None = None

    model_config = {"from_attributes": True}

    class Config:
        from_attributes = True

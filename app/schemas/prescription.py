from pydantic import BaseModel


class PrescriptionItemBase(BaseModel):
    medication_id: str | None = None
    medicamento_texto: str | None = None
    dosis: str
    horario: str
    via: str
    duracion: str
    instrucciones: str | None = None


class PrescriptionItemCreate(PrescriptionItemBase):
    pass


class PrescriptionItemOut(PrescriptionItemBase):
    id: str
    medication_nombre: str | None = None

    model_config = {"from_attributes": True}

    class Config:
        from_attributes = True

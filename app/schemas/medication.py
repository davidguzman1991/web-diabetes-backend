from pydantic import BaseModel


class MedicationBase(BaseModel):
    nombre_generico: str
    presentacion: str | None = None
    forma: str | None = None
    activo: bool = True


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    nombre_generico: str | None = None
    presentacion: str | None = None
    forma: str | None = None
    activo: bool | None = None


class MedicationOut(MedicationBase):
    id: str

    model_config = {"from_attributes": True}

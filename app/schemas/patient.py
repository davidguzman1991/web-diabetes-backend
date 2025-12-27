from datetime import date
from pydantic import BaseModel, EmailStr


class PatientBase(BaseModel):
    cedula: str
    apellidos: str
    nombres: str
    fecha_nacimiento: date
    email: EmailStr | None = None
    activo: bool = True


class PatientCreate(PatientBase):
    password: str | None = None


class PatientUpdate(BaseModel):
    apellidos: str | None = None
    nombres: str | None = None
    fecha_nacimiento: date | None = None
    email: EmailStr | None = None
    activo: bool | None = None


class PatientOut(PatientBase):
    id: str

    model_config = {"from_attributes": True}


class PatientLookupOut(BaseModel):
    id: str
    cedula: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date

    model_config = {"from_attributes": True}

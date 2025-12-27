from datetime import date
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


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

    model_config = ConfigDict(from_attributes=True)


class PatientLookupOut(BaseModel):
    id: str
    cedula: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date

    model_config = ConfigDict(from_attributes=True)


class ResetPatientPasswordRequest(BaseModel):
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 8:
            raise ValueError("new_password must be at least 8 characters")
        return cleaned

import uuid
from datetime import date
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    role: str = "admin"
    activo: bool = True


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    identifier: str
    password: str


class UserOut(UserBase):
    id: str

    model_config = {"from_attributes": True}


class PatientUserCreate(BaseModel):
    username: str
    password: str
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: date | None = None
    reset_password: bool = False

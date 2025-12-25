from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PatientLogin(BaseModel):
    cedula: str
    password: str


class AdminLogin(BaseModel):
    username: str
    password: str

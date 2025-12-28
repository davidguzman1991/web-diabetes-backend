from pydantic import BaseModel, ConfigDict


class DiagnosisBase(BaseModel):
    name: str
    cie10_code: str | None = None
    is_active: bool = True


class DiagnosisOut(DiagnosisBase):
    id: str

    model_config = ConfigDict(from_attributes=True)

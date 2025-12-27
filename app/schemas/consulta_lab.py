from datetime import datetime
from pydantic import BaseModel, field_validator, ConfigDict


class ConsultaLabCreate(BaseModel):
    lab_id: str
    valor_num: float | None = None

    @field_validator("lab_id")
    @classmethod
    def validate_lab_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Laboratorio requerido")
        return cleaned

    @field_validator("valor_num", mode="before")
    @classmethod
    def validate_valor_num(cls, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.strip().replace(",", ".")
            if not cleaned:
                return None
            try:
                return float(cleaned)
            except ValueError as exc:
                raise ValueError("El valor debe ser numerico") from exc
        return value

    @field_validator("valor_num", mode="after")
    @classmethod
    def ensure_valor_num(cls, value):
        if value is None:
            raise ValueError("El valor es requerido")
        return value


class ConsultaLabOut(BaseModel):
    id: str
    consulta_id: str
    lab_id: str
    lab_nombre: str
    valor_num: float | None = None
    valor_texto: str | None = None
    unidad_snapshot: str | None = None
    rango_ref_snapshot: str | None = None
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)

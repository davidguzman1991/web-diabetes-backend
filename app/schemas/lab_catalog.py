from pydantic import BaseModel, field_validator


class CatalogLabBase(BaseModel):
    nombre: str
    unidad: str | None = None
    rango_ref_min: float | None = None
    rango_ref_max: float | None = None
    categoria: str | None = None
    orden: int | None = None
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("nombre is required")
        return cleaned


class CatalogLabCreate(CatalogLabBase):
    pass


class CatalogLabUpdate(BaseModel):
    nombre: str | None = None
    unidad: str | None = None
    rango_ref_min: float | None = None
    rango_ref_max: float | None = None
    categoria: str | None = None
    orden: int | None = None
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("nombre is required")
        return cleaned


class CatalogLabOut(CatalogLabBase):
    id: str
    categoria: str | None = None
    orden: int | None = None

    model_config = {"from_attributes": True}

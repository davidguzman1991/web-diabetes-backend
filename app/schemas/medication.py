from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, AliasChoices


class MedicationBase(BaseModel):
    nombre_generico: str = Field(
        validation_alias=AliasChoices("nombre_generico", "generic_name")
    )
    presentacion: str | None = Field(
        default=None, validation_alias=AliasChoices("presentacion", "base_concentration")
    )
    forma: str | None = Field(default=None, validation_alias=AliasChoices("forma", "form"))
    activo: bool = Field(default=True, validation_alias=AliasChoices("activo", "is_active"))

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MedicationCreate(MedicationBase):
    pass


class MedicationCatalogCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    nombre_generico: str | None = Field(
        default=None, validation_alias=AliasChoices("nombre_generico", "generic_name")
    )
    presentacion: str | None = Field(
        default=None, validation_alias=AliasChoices("presentacion", "base_concentration")
    )
    forma: str | None = Field(
        default=None, validation_alias=AliasChoices("forma", "form")
    )
    activo: bool | None = Field(
        default=None, validation_alias=AliasChoices("activo", "is_active")
    )

    model_config = ConfigDict(populate_by_name=True)


class MedicationOut(MedicationBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

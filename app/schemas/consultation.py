from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, AliasChoices, field_validator, ConfigDict

from app.schemas.consultation_medication import MedicationCreate, MedicationOut


class ConsultationCreate(BaseModel):
    cedula: str
    fecha: date | datetime | None = None
    diagnosis: str | None = Field(
        default=None, validation_alias=AliasChoices("diagnostico", "diagnosis")
    )
    notes: str | None = Field(
        default=None, validation_alias=AliasChoices("notas", "notes")
    )
    indications: str | None = Field(
        default=None, validation_alias=AliasChoices("indicaciones", "indications")
    )
    medications: list[MedicationCreate]

    @field_validator("medications")
    @classmethod
    def validate_medications(cls, value: list[MedicationCreate]) -> list[MedicationCreate]:
        if not value:
            raise ValueError("medications must not be empty")
        return value

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ConsultationOut(BaseModel):
    id: UUID
    created_at: datetime
    diagnosis: str | None = Field(
        default=None, validation_alias=AliasChoices("diagnostico", "diagnosis")
    )
    notes: str | None = Field(
        default=None, validation_alias=AliasChoices("notas", "notes")
    )
    indications: str | None = Field(
        default=None, validation_alias=AliasChoices("indicaciones", "indications")
    )
    medications: list[MedicationOut]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ConsultationSummaryOut(BaseModel):
    id: UUID
    created_at: datetime
    diagnosis: str | None = Field(
        default=None, validation_alias=AliasChoices("diagnostico", "diagnosis")
    )
    indications: str | None = Field(
        default=None, validation_alias=AliasChoices("indicaciones", "indications")
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, AliasChoices, field_validator, ConfigDict

from app.schemas.consultation_medication import MedicationCreate, MedicationOut
from app.schemas.patient import PatientLookupOut


class ConsultationCreate(BaseModel):
    cedula: str
    fecha: date | datetime | None = None
    diagnosis: str | None = Field(
        default=None, validation_alias=AliasChoices("diagnostico", "diagnosis")
    )
    notes: str | None = Field(
        default=None, validation_alias=AliasChoices("notas", "notes", "notas_medicas")
    )
    indications: str | None = Field(
        default=None, validation_alias=AliasChoices("indicaciones", "indications")
    )
    weight: float | None = None
    height: float | None = None
    blood_pressure: str | None = None
    heart_rate: int | None = None
    oxygen_saturation: int | None = None
    abdominal_circumference: float | None = None
    reason_for_visit: str | None = Field(
        default=None, validation_alias=AliasChoices("motivo_consulta", "reason_for_visit")
    )
    current_illness: str | None = Field(
        default=None, validation_alias=AliasChoices("historia_actual", "current_illness")
    )
    physical_exam: str | None = Field(
        default=None, validation_alias=AliasChoices("examen_fisico", "physical_exam")
    )
    requested_exams: str | None = None
    next_visit_date: date | None = None
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
        default=None, validation_alias=AliasChoices("notas", "notes", "notas_medicas")
    )
    indications: str | None = Field(
        default=None, validation_alias=AliasChoices("indicaciones", "indications")
    )
    weight: float | None = None
    height: float | None = None
    blood_pressure: str | None = None
    heart_rate: int | None = None
    oxygen_saturation: int | None = None
    abdominal_circumference: float | None = None
    reason_for_visit: str | None = Field(
        default=None, validation_alias=AliasChoices("motivo_consulta", "reason_for_visit")
    )
    current_illness: str | None = Field(
        default=None, validation_alias=AliasChoices("historia_actual", "current_illness")
    )
    physical_exam: str | None = Field(
        default=None, validation_alias=AliasChoices("examen_fisico", "physical_exam")
    )
    requested_exams: str | None = None
    next_visit_date: date | None = None
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
    next_visit_date: date | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminConsultationMedicationOut(BaseModel):
    drug_name: str
    quantity: int | None = None
    description: str | None = None
    duration_days: int | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminConsultationDetailOut(BaseModel):
    id: UUID
    date: datetime
    diagnosis: str | None = None
    indications: str | None = None
    patient_full_name: str
    medications: list[AdminConsultationMedicationOut]

    model_config = ConfigDict(from_attributes=True)


class MedicationResponse(MedicationOut):
    model_config = ConfigDict(from_attributes=True)


class ConsultationResponse(BaseModel):
    id: UUID
    created_at: datetime
    patient: PatientLookupOut
    diagnosis: str | None = Field(
        default=None, validation_alias=AliasChoices("diagnostico", "diagnosis")
    )
    notes: str | None = Field(
        default=None, validation_alias=AliasChoices("notas", "notes", "notas_medicas")
    )
    indications: str | None = Field(
        default=None, validation_alias=AliasChoices("indicaciones", "indications")
    )
    weight: float | None = None
    height: float | None = None
    blood_pressure: str | None = None
    heart_rate: int | None = None
    oxygen_saturation: int | None = None
    abdominal_circumference: float | None = None
    reason_for_visit: str | None = Field(
        default=None, validation_alias=AliasChoices("motivo_consulta", "reason_for_visit")
    )
    current_illness: str | None = Field(
        default=None, validation_alias=AliasChoices("historia_actual", "current_illness")
    )
    physical_exam: str | None = Field(
        default=None, validation_alias=AliasChoices("examen_fisico", "physical_exam")
    )
    requested_exams: str | None = None
    next_visit_date: date | None = None
    medications: list[MedicationResponse]

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

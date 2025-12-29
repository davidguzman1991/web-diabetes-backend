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
    requested_exams: str | None = Field(
        default=None, validation_alias=AliasChoices("examenes_solicitados", "requested_exams")
    )
    next_visit_date: date | None = Field(
        default=None, validation_alias=AliasChoices("proxima_cita", "next_visit_date")
    )
    signos_vitales: dict | None = None
    laboratorios: list[dict] | None = None
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
    requested_exams: str | None = Field(
        default=None, validation_alias=AliasChoices("examenes_solicitados", "requested_exams")
    )
    next_visit_date: date | None = Field(
        default=None, validation_alias=AliasChoices("proxima_cita", "next_visit_date")
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


class ConsultationPatientOut(BaseModel):
    id: UUID | str
    cedula: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: date | None = None

    model_config = ConfigDict(from_attributes=True)


class ConsultationResponse(BaseModel):
    id: UUID
    created_at: datetime
    patient: ConsultationPatientOut | None = None
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
    requested_exams: str | None = Field(
        default=None, validation_alias=AliasChoices("examenes_solicitados", "requested_exams")
    )
    next_visit_date: date | None = Field(
        default=None, validation_alias=AliasChoices("proxima_cita", "next_visit_date")
    )
    diagnostico: str | None = None
    notas: str | None = None
    notas_medicas: str | None = None
    indicaciones: str | None = None
    motivo_consulta: str | None = None
    historia_actual: str | None = None
    examen_fisico: str | None = None
    examenes_solicitados: str | None = None
    proxima_cita: date | None = None
    signos_vitales: dict | None = None
    laboratorios: list[dict] = Field(default_factory=list)
    medications: list[MedicationResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

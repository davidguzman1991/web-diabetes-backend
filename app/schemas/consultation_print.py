from datetime import date, datetime
from pydantic import BaseModel


class PrintPatient(BaseModel):
    nombres: str
    apellidos: str
    cedula: str
    fecha_nacimiento: date


class PrintConsultation(BaseModel):
    created_at: datetime
    diagnosis: str | None = None
    notes: str | None = None
    indications: str | None = None


class PrintMedication(BaseModel):
    drug_name: str
    quantity: int | None = None
    description: str | None = None
    duration_days: int | None = None


class PrintLab(BaseModel):
    lab_nombre: str
    valor_num: float | None = None
    valor_texto: str | None = None
    unidad_snapshot: str | None = None
    rango_ref_snapshot: str | None = None


class ConsultationPrintOut(BaseModel):
    patient: PrintPatient
    consultation: PrintConsultation
    medications: list[PrintMedication]
    labs: list[PrintLab]

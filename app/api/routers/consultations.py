from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import consultations as consultation_crud
from app.crud import patients as patient_crud
from app.schemas.consultation_print import (
    ConsultationPrintOut,
    PrintConsultation,
    PrintLab,
    PrintMedication,
    PrintPatient,
)

router = APIRouter()


def _get_consultation_or_404(db: Session, consultation_id: str):
    consultation = consultation_crud.get(db, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consulta no existe")
    return consultation


def _ensure_access(db: Session, consultation, current_user) -> None:
    role = str(getattr(current_user, "role", "")).strip().lower()
    if role == "admin":
        return
    if role != "patient":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    patient = patient_crud.get_by_cedula(db, current_user.username)
    if not patient or str(patient.id) != str(consultation.patient_id):
        raise HTTPException(status_code=403, detail="Acceso denegado")


@router.get("/consultations/{consultation_id}/print", response_model=ConsultationPrintOut)
def get_consultation_print(
    consultation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    consultation = _get_consultation_or_404(db, consultation_id)
    _ensure_access(db, consultation, current_user)

    patient = patient_crud.get(db, consultation.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no existe")

    medications = [
        PrintMedication(
            drug_name=item.drug_name,
            dose=item.dose,
            frequency=item.frequency,
            route=item.route,
            duration=item.duration,
            indications=item.indications,
        )
        for item in consultation.medications
    ]

    labs_sorted = sorted(consultation.labs, key=lambda item: item.creado_en)
    labs = [
        PrintLab(
            lab_nombre=lab.lab.nombre if lab.lab else "",
            valor_num=lab.valor_num,
            valor_texto=lab.valor_texto,
            unidad_snapshot=lab.unidad_snapshot,
            rango_ref_snapshot=lab.rango_ref_snapshot,
        )
        for lab in labs_sorted
    ]

    return ConsultationPrintOut(
        patient=PrintPatient(
            nombres=patient.nombres,
            apellidos=patient.apellidos,
            cedula=patient.cedula,
            fecha_nacimiento=patient.fecha_nacimiento,
        ),
        consultation=PrintConsultation(
            created_at=consultation.created_at,
            diagnosis=consultation.diagnosis,
            notes=consultation.notes,
            indications=consultation.indications,
        ),
        medications=medications,
        labs=labs,
    )

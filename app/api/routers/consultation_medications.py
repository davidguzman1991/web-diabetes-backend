import logging
from typing import Iterable

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.dependencies import require_admin
from app.crud import consultation_medications as med_crud
from app.crud import consultations as consultation_crud
from app.crud import patients as patient_crud
from app.schemas.consultation_medication import MedicationCreate, MedicationOut, MedicationUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_patient_or_404(db: Session, patient_id: str):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no existe")
    return patient


def _get_consultation_or_404(db: Session, consultation_id: str, patient_id: str):
    consultation = consultation_crud.get(db, consultation_id)
    if not consultation or str(consultation.patient_id) != str(patient_id):
        raise HTTPException(status_code=404, detail="Consulta no existe")
    return consultation


def _ensure_patient_access(db: Session, patient_id: str, current_user) -> None:
    role = str(getattr(current_user, "role", "")).strip().lower()
    if role == "admin":
        return
    if role != "patient":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    patient = patient_crud.get_by_cedula(db, current_user.username)
    if not patient or str(patient.id) != str(patient_id):
        raise HTTPException(status_code=403, detail="Acceso denegado")


@router.get(
    "/patients/{patient_id}/consultations/{consultation_id}/medications",
    response_model=list[MedicationOut],
)
def list_consultation_medications(
    patient_id: str,
    consultation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_patient_access(db, patient_id, current_user)
    _get_patient_or_404(db, patient_id)
    _get_consultation_or_404(db, consultation_id, patient_id)
    return med_crud.list_by_consultation(db, consultation_id)


# Example payload:
# {
#   "drug_name": "Metformina",
#   "quantity": 30,
#   "description": "1 tableta cada 8 horas via oral despues de comidas",
#   "duration_days": 14,
#   "sort_order": 1
# }
@router.post(
    "/patients/{patient_id}/consultations/{consultation_id}/medications",
    response_model=list[MedicationOut],
    status_code=status.HTTP_201_CREATED,
)
def create_consultation_medications(
    patient_id: str,
    consultation_id: str,
    data: MedicationCreate | list[MedicationCreate],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    _get_patient_or_404(db, patient_id)
    _get_consultation_or_404(db, consultation_id, patient_id)
    items: Iterable[MedicationCreate] = data if isinstance(data, list) else [data]
    created = med_crud.create_many(db, consultation_id, items)
    logger.info("Created %s medications for consultation %s", len(created), consultation_id)
    return created


@router.put("/medications/{medication_id}", response_model=MedicationOut)
def update_medication(
    medication_id: str,
    data: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    medication = med_crud.get(db, medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento no existe")
    updated = med_crud.update(db, medication, data)
    logger.info("Updated medication %s", medication_id)
    return updated


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    medication = med_crud.get(db, medication_id)
    if not medication:
        raise HTTPException(status_code=404, detail="Medicamento no existe")
    med_crud.delete(db, medication)
    logger.info("Deleted medication %s", medication_id)
    return None


@router.get("/patients/{patient_id}/current-medications", response_model=list[MedicationOut])
def get_current_medications(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_patient_access(db, patient_id, current_user)
    _get_patient_or_404(db, patient_id)
    latest = consultation_crud.get_latest_by_patient(db, patient_id)
    if not latest:
        return []
    return med_crud.list_by_consultation(db, latest.id)

from datetime import datetime, time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import glucose_logs as glucose_crud
from app.crud import patient_tasks as task_crud
from app.crud import patients as patient_crud
from app.schemas.glucose import GlucoseLogCreate, GlucoseLogOut
from app.schemas.patient_task import PatientTaskOut

router = APIRouter()


def _get_patient_or_404(db: Session, patient_id: str):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no existe")
    return patient


def _ensure_patient_access(db: Session, patient_id: str, current_user) -> None:
    role = str(getattr(current_user, "role", "")).strip().lower()
    if role == "admin":
        return
    if role != "patient":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    patient = patient_crud.get_by_cedula(db, current_user.username)
    if not patient or str(patient.id) != str(patient_id):
        raise HTTPException(status_code=403, detail="Acceso denegado")


def _resolve_patient_id(db: Session, requested_id: str | None, current_user) -> str:
    role = str(getattr(current_user, "role", "")).strip().lower()
    if role == "admin":
        if not requested_id:
            raise HTTPException(status_code=400, detail="patient_id requerido")
        return requested_id
    if role != "patient":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    patient = patient_crud.get_by_cedula(db, current_user.username)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no existe")
    if requested_id and str(patient.id) != str(requested_id):
        raise HTTPException(status_code=403, detail="Acceso denegado")
    return str(patient.id)


def _resolve_glucose_type(data: GlucoseLogCreate) -> str:
    if data.measurement_type:
        if data.measurement_type == "fasting":
            return "ayuno"
        return "postprandial"
    if data.type:
        return data.type
    raise HTTPException(status_code=422, detail="measurement_type requerido")


def _resolve_taken_at(data: GlucoseLogCreate) -> datetime | None:
    if data.taken_at:
        return data.taken_at
    if data.date:
        return datetime.combine(data.date, time.min)
    return None


@router.post("/glucoses", response_model=GlucoseLogOut, status_code=status.HTTP_201_CREATED)
def create_glucose_log(
    data: GlucoseLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    role = str(getattr(current_user, "role", "")).strip().lower()
    requested_id = str(data.patient_id) if role == "admin" and data.patient_id else None
    patient_id = _resolve_patient_id(db, requested_id, current_user)
    _get_patient_or_404(db, patient_id)
    resolved_type = _resolve_glucose_type(data)
    taken_at = _resolve_taken_at(data)
    if not taken_at:
        raise HTTPException(status_code=422, detail="date requerido")
    return glucose_crud.create(db, patient_id, data.value, resolved_type, taken_at)


@router.get("/glucoses/patient/{patient_id}", response_model=list[GlucoseLogOut])
def list_glucose_logs(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _get_patient_or_404(db, patient_id)
    _ensure_patient_access(db, patient_id, current_user)
    return glucose_crud.list_by_patient(db, patient_id)


@router.get("/tasks/patient/{patient_id}", response_model=list[PatientTaskOut])
def list_patient_tasks(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _get_patient_or_404(db, patient_id)
    _ensure_patient_access(db, patient_id, current_user)
    return task_crud.list_by_patient(db, patient_id)


@router.post("/tasks/{task_id}/complete", response_model=PatientTaskOut)
def complete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = task_crud.get(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no existe")
    _ensure_patient_access(db, str(task.patient_id), current_user)
    return task_crud.mark_complete(db, task)

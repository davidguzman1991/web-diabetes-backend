from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.dependencies import require_patient
from app.crud import visits as visit_crud
from app.crud import consultas as consulta_crud
from app.crud import consultations as consultation_crud
from app.crud import patients as patient_crud
from app.models.patient import Patient
from app.schemas.consulta import ConsultaOut, ConsultaSummary
from app.schemas.consultation import ConsultationOut
from app.schemas.visit import VisitListItem, VisitOut

router = APIRouter(dependencies=[Depends(require_patient)])


def get_patient_id(current_user) -> str:
    return str(current_user.id)


def get_patient_by_user(db: Session, current_user):
    patient = None
    try:
        patient = (
            db.query(Patient)
            .filter(text("patients.user_id = :user_id"))
            .params(user_id=str(current_user.id))
            .first()
        )
    except SQLAlchemyError:
        patient = None

    if not patient:
        patient = patient_crud.get_by_cedula(db, current_user.username)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found for this user")
    return patient


@router.get("/me/current-medication", response_model=VisitOut | None)
def get_current_medication(current_user = Depends(require_patient), db: Session = Depends(get_db)):
    patient_id = get_patient_id(current_user)
    visits = visit_crud.list_by_patient(db, patient_id)
    return visits[0] if visits else None


@router.get("/me/visits", response_model=list[VisitListItem])
def list_my_visits(current_user = Depends(require_patient), db: Session = Depends(get_db)):
    patient_id = get_patient_id(current_user)
    return visit_crud.list_by_patient(db, patient_id)


@router.get("/me/visits/{visit_id}", response_model=VisitOut)
def get_my_visit(visit_id: str, current_user = Depends(require_patient), db: Session = Depends(get_db)):
    patient_id = get_patient_id(current_user)
    visit = visit_crud.get(db, visit_id)
    if not visit or str(visit.patient_id) != patient_id:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.get("/portal")
def patient_portal(current_user = Depends(require_patient)):
    return {"message": "Patient portal", "patient_id": str(current_user.id)}


@router.get("/consultas", response_model=list[ConsultaSummary])
def list_consultas(current_user = Depends(require_patient), db: Session = Depends(get_db)):
    return consulta_crud.list_by_patient_user(db, get_patient_id(current_user))


@router.get("/consultations", response_model=list[ConsultationOut])
def list_consultations(current_user = Depends(require_patient), db: Session = Depends(get_db)):
    patient = get_patient_by_user(db, current_user)
    return consultation_crud.list_by_patient(db, patient.id)


@router.get("/consultations/{consultation_id}", response_model=ConsultationOut)
def get_consultation(consultation_id: str, current_user = Depends(require_patient), db: Session = Depends(get_db)):
    patient = get_patient_by_user(db, current_user)
    consultation = consultation_crud.get(db, consultation_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consulta no existe")
    if str(consultation.patient_id) != str(patient.id):
        raise HTTPException(status_code=403, detail="Not allowed")
    return consultation


@router.get("/medication/current", response_model=ConsultationOut | None)
def get_current_consultation(current_user = Depends(require_patient), db: Session = Depends(get_db)):
    patient = get_patient_by_user(db, current_user)
    return consultation_crud.get_latest_by_patient(db, patient.id)


@router.get("/consultas/{consulta_id}", response_model=ConsultaOut)
def get_consulta(consulta_id: str, current_user = Depends(require_patient), db: Session = Depends(get_db)):
    consulta = consulta_crud.get(db, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta not found")
    if str(consulta.patient_user_id) != get_patient_id(current_user):
        raise HTTPException(status_code=403, detail="Not allowed")
    return consulta


@router.get("/medicacion-actual", response_model=ConsultaOut)
def get_current_consulta(current_user = Depends(require_patient), db: Session = Depends(get_db)):
    consulta = consulta_crud.get_latest_by_patient(db, get_patient_id(current_user))
    if not consulta:
        raise HTTPException(status_code=404, detail="No hay consultas registradas")
    return consulta

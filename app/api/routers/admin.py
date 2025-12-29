import json
import logging
from datetime import date, datetime, time
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.core.config import settings
from app.core.dependencies import require_admin
from app.core.security import get_password_hash
from app.crud import patients as patient_crud
from app.crud import diagnoses as diagnosis_crud
from app.crud import medications as medication_crud
from app.crud import visits as visit_crud
from app.crud import consultas as consulta_crud
from app.crud import consultations as consultation_crud
from app.models.consultation import Consultation
from app.models.consulta_lab import ConsultaLab
from app.models.consultation_medication import Medication
from app.models.medication import MedicationCatalog
from app.models.user import User
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientOut,
    PatientLookupOut,
    ResetPatientPasswordRequest,
)
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationOut
from app.schemas.visit import VisitCreate, VisitOut, VisitListItem
from app.schemas.consulta import ConsultaCreate, ConsultaOut, ConsultaSummary
from app.schemas.consultation import ConsultationCreate, ConsultationOut, ConsultationResponse
from app.schemas.user import PatientUserCreate, UserOut
from app.schemas.diagnosis import DiagnosisOut

router = APIRouter(dependencies=[Depends(require_admin)])
logger = logging.getLogger(__name__)
get_current_admin = require_admin


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _int_to_text(value: int | None) -> str | None:
    if value is None:
        return None
    return str(int(value))


def _parse_signos_vitales(value) -> dict:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _pick_signo(signos: dict, *keys: str):
    for key in keys:
        if key in signos:
            return signos[key]
    return None


def _coerce_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_str(value):
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _resolve_medication_id(db: Session, medication_id: str | None, drug_name: str) -> str | None:
    if medication_id:
        return medication_id
    cleaned = (drug_name or "").strip()
    if not cleaned:
        return None
    return (
        db.query(MedicationCatalog.id)
        .filter(func.lower(MedicationCatalog.nombre_generico) == cleaned.lower())
        .scalar()
    )


def _serialize_consultation(consultation: Consultation) -> dict:
    return {
        "id": str(consultation.id),
        "created_at": consultation.created_at,
        "diagnosis": consultation.diagnosis,
        "notes": consultation.notes,
        "indications": consultation.indications,
        "weight": consultation.weight,
        "height": consultation.height,
        "blood_pressure": consultation.blood_pressure,
        "heart_rate": consultation.heart_rate,
        "oxygen_saturation": consultation.oxygen_saturation,
        "abdominal_circumference": consultation.abdominal_circumference,
        "reason_for_visit": consultation.reason_for_visit,
        "current_illness": consultation.current_illness,
        "physical_exam": consultation.physical_exam,
        "requested_exams": consultation.requested_exams,
        "next_visit_date": consultation.next_visit_date,
        "medications": [
            {
                "id": str(med.id),
                "consultation_id": str(med.consultation_id),
                "medication_id": str(med.medication_id) if med.medication_id else None,
                "drug_name": med.drug_name,
                "quantity": med.quantity,
                "description": med.description,
                "duration_days": med.duration_days,
                "sort_order": med.sort_order,
                "created_at": med.created_at,
                "updated_at": med.updated_at,
            }
            for med in consultation.medications
        ],
    }


@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


def _get_patient_user(db: Session, username: str) -> User:
    user = db.query(User).filter(User.username == username).first()
    if not user or user.role.lower() != "patient":
        raise HTTPException(status_code=404, detail="Patient not found")
    return user


def _get_patient(db: Session, cedula: str):
    patient = patient_crud.get_by_cedula(db, cedula)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient not found for cedula {cedula}")
    return patient


@router.get("/patients", response_model=PatientLookupOut | list[PatientOut])
def list_patients(cedula: str | None = None, db: Session = Depends(get_db)):
    try:
        if cedula:
            patient = patient_crud.get_by_cedula(db, cedula)
            if not patient:
                raise HTTPException(status_code=404, detail="Paciente no existe")
            return PatientLookupOut(
                id=str(patient.id),
                cedula=patient.cedula,
                nombres=patient.nombres,
                apellidos=patient.apellidos,
                fecha_nacimiento=patient.fecha_nacimiento,
            )
        return patient_crud.list_patients(db)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to list patients", extra={"cedula": cedula})
        raise HTTPException(status_code=500, detail="Error fetching patients") from exc


@router.post("/patients", response_model=PatientOut | UserOut, status_code=status.HTTP_201_CREATED)
def create_patient(data: PatientCreate | PatientUserCreate, db: Session = Depends(get_db)):
    if isinstance(data, PatientUserCreate):
        user = db.query(User).filter(User.username == data.username).first()
        if user:
            if not data.reset_password:
                raise HTTPException(status_code=409, detail="Username already exists")
            user.password_hash = get_password_hash(data.password)
            user.role = "patient"
            user.activo = True
            db.commit()
            db.refresh(user)
            return UserOut(id=str(user.id), username=user.username, role=user.role, activo=bool(user.activo))

        user = User(
            username=data.username,
            password_hash=get_password_hash(data.password),
            role="patient",
            activo=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserOut(id=str(user.id), username=user.username, role=user.role, activo=bool(user.activo))

    existing = patient_crud.get_by_cedula(db, data.cedula)
    if existing:
        raise HTTPException(status_code=409, detail="Cedula already exists")

    seed = data.password or patient_crud.normalize_password_seed(data.apellidos, data.nombres)
    password_hash = get_password_hash(seed)
    try:
        patient = patient_crud.create(db, data, password_hash=password_hash, commit=False)

        username = data.cedula
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.password_hash = password_hash
            user.role = "patient"
            user.activo = True
        else:
            user = User(
                username=username,
                password_hash=password_hash,
                role="patient",
                activo=True,
            )
            db.add(user)

        db.commit()
        db.refresh(patient)
        return patient
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cedula already exists") from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to create patient", extra={"cedula": data.cedula})
        raise HTTPException(status_code=500, detail="Error creating patient") from exc


@router.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/patients/{patient_id}/reset-password")
def reset_patient_password(
    patient_id: str,
    data: ResetPatientPasswordRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        new_hash = get_password_hash(data.new_password)
        patient.password_hash = new_hash
        user = db.query(User).filter(User.username == patient.cedula).first()
        if user and user.role.lower() == "patient":
            user.password_hash = new_hash
            user.activo = True
        db.commit()
        return {"success": True}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error") from exc


@router.put("/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: str, data: PatientUpdate, db: Session = Depends(get_db)):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_crud.update(db, patient, data)


@router.delete("/patients/{patient_id}", response_model=PatientOut)
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_crud.deactivate(db, patient)


@router.get("/medications", response_model=list[MedicationOut])
def list_medications(db: Session = Depends(get_db)):
    return medication_crud.list_all(db)

@router.get("/medications/autocomplete", response_model=list[MedicationOut])
def autocomplete_medications(q: str = "", db: Session = Depends(get_db)):
    return medication_crud.autocomplete(db, q)


@router.post("/medications", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication(data: MedicationCreate, db: Session = Depends(get_db)):
    existing = medication_crud.get_by_generic_name(db, data.nombre_generico)
    if existing:
        raise HTTPException(status_code=409, detail="Medication already exists")
    return medication_crud.create(db, data)


@router.put("/medications/{med_id}", response_model=MedicationOut)
def update_medication(med_id: str, data: MedicationUpdate, db: Session = Depends(get_db)):
    med = medication_crud.get(db, med_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    if data.nombre_generico:
        existing = medication_crud.get_by_generic_name(db, data.nombre_generico)
        if existing and str(existing.id) != str(med.id):
            raise HTTPException(status_code=409, detail="Medication already exists")
    return medication_crud.update(db, med, data)


@router.delete("/medications/{med_id}", response_model=MedicationOut)
def delete_medication(med_id: str, db: Session = Depends(get_db)):
    med = medication_crud.get(db, med_id)
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return medication_crud.deactivate(db, med)


@router.get("/diagnoses/autocomplete", response_model=list[DiagnosisOut])
def autocomplete_diagnoses(q: str = "", db: Session = Depends(get_db)):
    return diagnosis_crud.autocomplete(db, q)


@router.get("/patients/{patient_id}/visits", response_model=list[VisitListItem])
def list_visits(patient_id: str, db: Session = Depends(get_db)):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return visit_crud.list_by_patient(db, patient_id)


@router.post("/patients/{patient_id}/visits", response_model=VisitOut, status_code=status.HTTP_201_CREATED)
def create_visit(patient_id: str, data: VisitCreate, db: Session = Depends(get_db)):
    patient = patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for item in data.items:
        if not item.medication_id and not item.medicamento_texto:
            raise HTTPException(status_code=400, detail="Medication or free text required")
        if item.medication_id:
            med = medication_crud.get(db, item.medication_id)
            if not med:
                raise HTTPException(status_code=400, detail="Medication not found")

    return visit_crud.create(db, patient_id, data)


@router.get("/visits/{visit_id}", response_model=VisitOut)
def get_visit(visit_id: str, db: Session = Depends(get_db)):
    visit = visit_crud.get(db, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return visit


@router.post("/patients/{patient_username}/consultas", response_model=ConsultaOut, status_code=status.HTTP_201_CREATED)
def create_consulta(
    patient_username: str,
    data: ConsultaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    patient_user = _get_patient_user(db, patient_username)
    return consulta_crud.create(db, patient_user.id, current_user.id, data)


@router.post("/consultations", response_model=ConsultationOut, status_code=status.HTTP_201_CREATED)
def create_consultation(data: ConsultationCreate, db: Session = Depends(get_db)):
    patient = patient_crud.get_by_cedula(db, data.cedula)
    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Paciente no encontrado para cedula {data.cedula}",
        )

    try:
        created_at = None
        if getattr(data, "fecha", None) is not None:
            if isinstance(data.fecha, datetime):
                created_at = data.fecha
            elif isinstance(data.fecha, date):
                created_at = datetime.combine(data.fecha, time.min)
            elif isinstance(data.fecha, str):
                try:
                    created_at = datetime.combine(date.fromisoformat(data.fecha), time.min)
                except ValueError as exc:
                    raise HTTPException(
                        status_code=400,
                        detail="Fecha invalida, usa YYYY-MM-DD",
                    ) from exc

        signos = _parse_signos_vitales(getattr(data, "signos_vitales", None))
        weight_value = (
            data.weight
            if data.weight is not None
            else _coerce_float(_pick_signo(signos, "weight", "peso"))
        )
        height_value = (
            data.height
            if data.height is not None
            else _coerce_float(_pick_signo(signos, "height", "talla"))
        )
        blood_pressure_value = (
            data.blood_pressure
            if data.blood_pressure is not None
            else _coerce_str(_pick_signo(signos, "blood_pressure", "presion_arterial"))
        )
        heart_rate_value = (
            data.heart_rate
            if data.heart_rate is not None
            else _coerce_int(_pick_signo(signos, "heart_rate", "frecuencia_cardiaca"))
        )
        oxygen_value = (
            data.oxygen_saturation
            if data.oxygen_saturation is not None
            else _coerce_int(_pick_signo(signos, "oxygen_saturation", "saturacion_oxigeno"))
        )
        abdominal_value = (
            data.abdominal_circumference
            if data.abdominal_circumference is not None
            else _coerce_float(_pick_signo(signos, "abdominal_circumference", "circunferencia_abdominal"))
        )

        diagnosis = _normalize_text(data.diagnosis) or _normalize_text(getattr(data, "diagnostico", None))
        notes = (
            _normalize_text(data.notes)
            or _normalize_text(getattr(data, "notas_medicas", None))
            or _normalize_text(getattr(data, "notas", None))
        )
        indications = _normalize_text(data.indications) or _normalize_text(
            getattr(data, "indicaciones", None)
        )
        reason_for_visit = _normalize_text(data.reason_for_visit) or _normalize_text(
            getattr(data, "motivo_consulta", None)
        )
        current_illness = _normalize_text(data.current_illness) or _normalize_text(
            getattr(data, "historia_actual", None)
        )
        physical_exam = _normalize_text(data.physical_exam) or _normalize_text(
            getattr(data, "examen_fisico", None)
        )
        requested_exams = _normalize_text(data.requested_exams) or _normalize_text(
            getattr(data, "examenes_solicitados", None)
        )
        next_visit_date = data.next_visit_date or getattr(data, "proxima_cita", None)

        consultation_fields = {
            "patient_id": patient.id,
            "diagnosis": diagnosis,
            "notes": notes,
            "indications": indications,
            "weight": weight_value,
            "height": height_value,
            "blood_pressure": blood_pressure_value,
            "heart_rate": heart_rate_value,
            "oxygen_saturation": oxygen_value,
            "abdominal_circumference": abdominal_value,
            "reason_for_visit": reason_for_visit,
            "current_illness": current_illness,
            "physical_exam": physical_exam,
            "requested_exams": requested_exams,
            "next_visit_date": next_visit_date,
        }
        if created_at is not None:
            consultation_fields["created_at"] = created_at

        consultation = Consultation(**consultation_fields)
        db.add(consultation)
        db.flush()
        diagnosis_crud.ensure(db, data.diagnosis)

        for index, item in enumerate(data.medications):
            sort_order = item.sort_order if item.sort_order is not None else index
            medication = Medication(
                consultation_id=consultation.id,
                medication_id=_resolve_medication_id(db, item.medication_id, item.drug_name),
                drug_name=item.drug_name,
                dose=_int_to_text(item.quantity),
                route=None,
                frequency=None,
                duration=_int_to_text(item.duration_days),
                indications=_normalize_text(item.description),
                sort_order=sort_order,
            )
            db.add(medication)
            consultation.medications.append(medication)

        db.commit()
        db.refresh(consultation)
        return _serialize_consultation(consultation)
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        logger.exception("Integrity error creating consultation")
        raise HTTPException(
            status_code=409, detail="Integrity error creating consultation"
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("create_consultation failed", extra={"cedula": data.cedula})
        detail = "Internal Server Error"
        if str(settings.ENV).lower() == "development":
            detail = f"{type(exc).__name__}: {exc}"
        raise HTTPException(status_code=500, detail=detail) from exc


@router.get("/consultations", response_model=list[ConsultationOut])
def list_consultations(cedula: str, db: Session = Depends(get_db)):
    patient = _get_patient(db, cedula)
    consultations = consultation_crud.list_by_patient(db, patient.id)
    return [_serialize_consultation(item) for item in consultations]


@router.get("/consultations/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: UUID,
    db: Session = Depends(get_db),
    _current_admin=Depends(get_current_admin),
):
    logger.info("Fetching consultation %s", consultation_id)
    try:
        consultation = (
            db.query(Consultation)
            .options(
                joinedload(Consultation.medications),
                joinedload(Consultation.patient),
                joinedload(Consultation.labs).joinedload(ConsultaLab.lab),
            )
            .filter(Consultation.id == consultation_id)
            .first()
        )
        if not consultation:
            logger.info("Consultation not found %s", consultation_id)
            raise HTTPException(status_code=404, detail="Consultation not found")
        return consultation
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to fetch consultation %s", consultation_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")



@router.get("/patients/{cedula}/current-medications", response_model=ConsultationOut)
def get_current_medications(cedula: str, db: Session = Depends(get_db)):
    patient = _get_patient(db, cedula)
    consultation = consultation_crud.get_latest_by_patient(db, patient.id)
    if not consultation:
        raise HTTPException(status_code=404, detail="No hay consultas registradas")
    return _serialize_consultation(consultation)


@router.get("/patients/{patient_username}/consultas", response_model=list[ConsultaSummary])
def list_consultas_by_patient(
    patient_username: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    patient_user = _get_patient_user(db, patient_username)
    return consulta_crud.list_by_patient_user(db, patient_user.id)


@router.get("/consultas/{consulta_id}", response_model=ConsultaOut)
def get_consulta(consulta_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    consulta = consulta_crud.get(db, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta not found")
    return consulta


@router.get("/consultations/{consulta_id}/print", response_class=HTMLResponse)
def print_consultation(consulta_id: str, db: Session = Depends(get_db)):
    consultation = consultation_crud.get(db, consulta_id)
    if not consultation:
        raise HTTPException(status_code=404, detail="Consulta no existe")

    patient = patient_crud.get(db, consultation.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente no existe")

    meds_html = "".join(
        f"<tr><td>{med.drug_name}</td><td>{med.quantity or ''}</td><td>{med.description or ''}</td>"
        f"<td>{f'{med.duration_days} dias' if med.duration_days is not None else ''}</td></tr>"
        for med in consultation.medications
    )

    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Consulta</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 24px; color: #111; }}
          h1, h2 {{ margin: 0 0 12px 0; }}
          .muted {{ color: #666; font-size: 12px; }}
          table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
          th {{ background: #f5f5f5; }}
        </style>
      </head>
      <body>
        <h1>Consulta Clinica</h1>
        <div class="muted">Fecha: {consultation.created_at.date()}</div>
        <h2>Paciente</h2>
        <div>{patient.nombres} {patient.apellidos} - Cedula: {patient.cedula}</div>
        <h2>Consulta</h2>
        <div><strong>Diagnostico:</strong> {consultation.diagnosis or ''}</div>
        <div><strong>Notas:</strong> {consultation.notes or ''}</div>
        <div><strong>Indicaciones:</strong> {consultation.indications or ''}</div>
        <h2>Medicamentos</h2>
        <table>
          <thead>
            <tr>
              <th>Medicamento</th>
              <th>Cantidad</th>
              <th>Descripcion</th>
              <th>Duracion (dias)</th>
            </tr>
          </thead>
          <tbody>
            {meds_html}
          </tbody>
        </table>
      </body>
    </html>
    """
    return HTMLResponse(content=html)

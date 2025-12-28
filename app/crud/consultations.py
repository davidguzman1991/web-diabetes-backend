import logging
from datetime import date, datetime, time

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud import diagnoses as diagnosis_crud
from app.models.consultation import Consultation
from app.models.consultation_medication import Medication
from app.models.medication import MedicationCatalog

logger = logging.getLogger(__name__)


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _int_to_text(value: int | None) -> str | None:
    if value is None:
        return None
    return str(int(value))


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


def _normalize_fecha(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            if "T" in cleaned or " " in cleaned:
                return datetime.fromisoformat(cleaned)
            return datetime.combine(date.fromisoformat(cleaned), time.min)
        except ValueError as exc:
            raise ValueError("fecha invalida, usa YYYY-MM-DD") from exc
    return None


def list_by_patient(db: Session, patient_id: str) -> list[Consultation]:
    return (
        db.query(Consultation)
        .filter(Consultation.patient_id == patient_id)
        .order_by(Consultation.created_at.desc())
        .all()
    )


def get(db: Session, consultation_id: str) -> Consultation | None:
    return db.query(Consultation).filter(Consultation.id == consultation_id).first()


def get_latest_by_patient(db: Session, patient_id: str) -> Consultation | None:
    return (
        db.query(Consultation)
        .filter(Consultation.patient_id == patient_id)
        .order_by(Consultation.created_at.desc())
        .first()
    )


def create(db: Session, patient_id: str, data) -> Consultation:
    try:
        created_at = _normalize_fecha(getattr(data, "fecha", None))
        consultation_data = {
            "patient_id": patient_id,
            "diagnosis": data.diagnosis,
            "notes": data.notes,
            "indications": data.indications,
            "weight": getattr(data, "weight", None),
            "height": getattr(data, "height", None),
            "blood_pressure": getattr(data, "blood_pressure", None),
            "heart_rate": getattr(data, "heart_rate", None),
            "oxygen_saturation": getattr(data, "oxygen_saturation", None),
            "abdominal_circumference": getattr(data, "abdominal_circumference", None),
            "reason_for_visit": getattr(data, "reason_for_visit", None),
            "current_illness": getattr(data, "current_illness", None),
            "physical_exam": getattr(data, "physical_exam", None),
            "requested_exams": getattr(data, "requested_exams", None),
            "next_visit_date": getattr(data, "next_visit_date", None),
        }
        if created_at is not None:
            consultation_data["created_at"] = created_at
        consultation = Consultation(**consultation_data)
        db.add(consultation)
        db.flush()
        diagnosis_crud.ensure(db, data.diagnosis)
        logger.info("Creating consultation %s for patient %s", consultation.id, patient_id)

        for index, item in enumerate(data.medications):
            sort_order = item.sort_order if item.sort_order is not None else index
            db.add(
                Medication(
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
            )

        logger.info("Committing consultation %s", consultation.id)
        db.commit()
        db.refresh(consultation)
        logger.info("Committed consultation %s", consultation.id)
        return consultation
    except IntegrityError:
        db.rollback()
        logger.exception("Integrity error creating consultation for patient %s", patient_id)
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error creating consultation for patient %s", patient_id)
        raise

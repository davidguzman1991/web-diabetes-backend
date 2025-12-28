from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.consultation_medication import Medication
from app.models.medication import MedicationCatalog


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


def list_by_consultation(db: Session, consultation_id: str) -> list[Medication]:
    return (
        db.query(Medication)
        .filter(Medication.consultation_id == consultation_id)
        .order_by(Medication.sort_order.asc(), Medication.created_at.asc())
        .all()
    )


def get(db: Session, medication_id: str) -> Medication | None:
    return db.query(Medication).filter(Medication.id == medication_id).first()


def create_many(db: Session, consultation_id: str, items) -> list[Medication]:
    created: list[Medication] = []
    for index, item in enumerate(items):
        created.append(
            Medication(
                consultation_id=consultation_id,
                medication_id=_resolve_medication_id(db, item.medication_id, item.drug_name),
                drug_name=item.drug_name,
                dose=_int_to_text(item.quantity),
                route=None,
                frequency=None,
                duration=_int_to_text(item.duration_days),
                indications=_normalize_text(item.description),
                sort_order=item.sort_order if item.sort_order is not None else index,
            )
        )
    db.add_all(created)
    db.commit()
    for med in created:
        db.refresh(med)
    return created


def update(db: Session, medication: Medication, data) -> Medication:
    payload = data.model_dump(exclude_unset=True)
    if "medication_id" in payload:
        medication.medication_id = payload["medication_id"]
    if "drug_name" in payload:
        medication.drug_name = payload["drug_name"]
    if "quantity" in payload:
        medication.dose = _int_to_text(payload["quantity"])
    if "duration_days" in payload:
        medication.duration = _int_to_text(payload["duration_days"])
    if "description" in payload:
        medication.indications = _normalize_text(payload["description"])
    if "sort_order" in payload:
        medication.sort_order = payload["sort_order"]
    if any(key in payload for key in ("drug_name", "quantity", "duration_days", "description")):
        medication.route = None
        medication.frequency = None
    db.commit()
    db.refresh(medication)
    return medication


def delete(db: Session, medication: Medication) -> None:
    db.delete(medication)
    db.commit()

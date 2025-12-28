from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.medication import MedicationCatalog


def get(db: Session, med_id: str) -> MedicationCatalog | None:
    return db.query(MedicationCatalog).filter(MedicationCatalog.id == med_id).first()

def get_by_generic_name(db: Session, name: str) -> MedicationCatalog | None:
    cleaned = (name or "").strip()
    if not cleaned:
        return None
    return (
        db.query(MedicationCatalog)
        .filter(func.lower(MedicationCatalog.nombre_generico) == cleaned.lower())
        .first()
    )


def list_all(db: Session) -> list[MedicationCatalog]:
    return db.query(MedicationCatalog).order_by(MedicationCatalog.nombre_generico.asc()).all()

def autocomplete(db: Session, query: str, limit: int = 20) -> list[MedicationCatalog]:
    cleaned = (query or "").strip()
    if not cleaned:
        return []
    pattern = f"%{cleaned}%"
    return (
        db.query(MedicationCatalog)
        .filter(MedicationCatalog.activo.is_(True))
        .filter(MedicationCatalog.nombre_generico.ilike(pattern))
        .order_by(MedicationCatalog.nombre_generico.asc())
        .limit(limit)
        .all()
    )


def create(db: Session, data) -> MedicationCatalog:
    med = MedicationCatalog(
        nombre_generico=data.nombre_generico,
        presentacion=data.presentacion,
        forma=data.forma,
        activo=data.activo,
    )
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


def update(db: Session, med: MedicationCatalog, data) -> MedicationCatalog:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(med, field, value)
    db.commit()
    db.refresh(med)
    return med


def deactivate(db: Session, med: MedicationCatalog) -> MedicationCatalog:
    med.activo = False
    db.commit()
    db.refresh(med)
    return med

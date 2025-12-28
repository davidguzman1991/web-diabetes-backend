from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.diagnosis import DiagnosisCatalog


def ensure(db: Session, name: str | None) -> DiagnosisCatalog | None:
    cleaned = (name or "").strip()
    if not cleaned:
        return None
    existing = (
        db.query(DiagnosisCatalog)
        .filter(func.lower(DiagnosisCatalog.name) == cleaned.lower())
        .first()
    )
    if existing:
        return existing
    diagnosis = DiagnosisCatalog(name=cleaned)
    db.add(diagnosis)
    db.flush()
    return diagnosis


def autocomplete(db: Session, query: str, limit: int = 20) -> list[DiagnosisCatalog]:
    cleaned = (query or "").strip()
    if not cleaned:
        return []
    pattern = f"%{cleaned}%"
    return (
        db.query(DiagnosisCatalog)
        .filter(DiagnosisCatalog.is_active.is_(True))
        .filter(DiagnosisCatalog.name.ilike(pattern))
        .order_by(DiagnosisCatalog.name.asc())
        .limit(limit)
        .all()
    )

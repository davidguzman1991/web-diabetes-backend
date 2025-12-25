from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.catalog_lab import CatalogLab


def list_catalog(db: Session) -> list[CatalogLab]:
    return (
        db.query(CatalogLab)
        .filter(CatalogLab.activo.is_(True))
        .order_by(CatalogLab.orden.asc(), CatalogLab.nombre.asc())
        .all()
    )


def get(db: Session, lab_id: str) -> CatalogLab | None:
    return db.query(CatalogLab).filter(CatalogLab.id == lab_id).first()


def get_by_name(db: Session, nombre: str) -> CatalogLab | None:
    return db.query(CatalogLab).filter(CatalogLab.nombre == nombre).first()


def _normalize_name(nombre: str) -> str:
    return " ".join((nombre or "").strip().split())


def get_by_name_normalized(db: Session, nombre: str) -> CatalogLab | None:
    normalized = _normalize_name(nombre)
    if not normalized:
        return None
    lowered = normalized.lower()
    return db.query(CatalogLab).filter(func.lower(CatalogLab.nombre) == lowered).first()


def find_by_name_contains(db: Session, nombre: str) -> CatalogLab | None:
    normalized = _normalize_name(nombre)
    if not normalized:
        return None
    lowered = normalized.lower()
    return (
        db.query(CatalogLab)
        .filter(func.lower(CatalogLab.nombre).like(f"%{lowered}%"))
        .order_by(CatalogLab.nombre.asc())
        .first()
    )


def create(db: Session, data) -> CatalogLab:
    lab = CatalogLab(
        nombre=data.nombre,
        unidad=data.unidad,
        rango_ref_min=data.rango_ref_min,
        rango_ref_max=data.rango_ref_max,
        categoria=getattr(data, "categoria", None),
        orden=getattr(data, "orden", None) or 0,
        activo=data.activo,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


def update(db: Session, lab: CatalogLab, data) -> CatalogLab:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lab, field, value)
    db.commit()
    db.refresh(lab)
    return lab

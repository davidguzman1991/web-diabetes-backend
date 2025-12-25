from sqlalchemy.orm import Session

from app.models.medication import MedicationCatalog


def get(db: Session, med_id: str) -> MedicationCatalog | None:
    return db.query(MedicationCatalog).filter(MedicationCatalog.id == med_id).first()


def list_all(db: Session) -> list[MedicationCatalog]:
    return db.query(MedicationCatalog).order_by(MedicationCatalog.nombre_generico.asc()).all()


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

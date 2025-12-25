from sqlalchemy.orm import Session

from app.models.consulta_lab import ConsultaLab


def list_by_consulta(db: Session, consulta_id: str) -> list[ConsultaLab]:
    return (
        db.query(ConsultaLab)
        .filter(ConsultaLab.consulta_id == consulta_id)
        .order_by(ConsultaLab.creado_en.asc())
        .all()
    )


def delete_by_consulta(db: Session, consulta_id: str) -> None:
    db.query(ConsultaLab).filter(ConsultaLab.consulta_id == consulta_id).delete()
    db.commit()


def create_many(db: Session, items: list[ConsultaLab]) -> list[ConsultaLab]:
    db.add_all(items)
    db.commit()
    for item in items:
        db.refresh(item)
    return items

from sqlalchemy.orm import Session

from app.models.consultation_medication import Medication


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
                drug_name=item.drug_name,
                dose=item.dose,
                route=item.route,
                frequency=item.frequency,
                duration=item.duration,
                indications=item.indications,
                sort_order=item.sort_order if item.sort_order is not None else index,
            )
        )
    db.add_all(created)
    db.commit()
    for med in created:
        db.refresh(med)
    return created


def update(db: Session, medication: Medication, data) -> Medication:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(medication, field, value)
    db.commit()
    db.refresh(medication)
    return medication


def delete(db: Session, medication: Medication) -> None:
    db.delete(medication)
    db.commit()

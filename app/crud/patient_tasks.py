from datetime import datetime
from sqlalchemy.orm import Session

from app.models.patient_task import PatientTask


def get(db: Session, task_id: str) -> PatientTask | None:
    return db.query(PatientTask).filter(PatientTask.id == task_id).first()


def list_by_patient(db: Session, patient_id: str) -> list[PatientTask]:
    return (
        db.query(PatientTask)
        .filter(PatientTask.patient_id == patient_id)
        .order_by(PatientTask.created_at.desc())
        .all()
    )


def mark_complete(db: Session, task: PatientTask) -> PatientTask:
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task

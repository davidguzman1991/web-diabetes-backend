from datetime import datetime
from sqlalchemy.orm import Session

from app.models.glucose_log import GlucoseLog


def create(
    db: Session,
    patient_id: str,
    value: int,
    type_value: str,
    taken_at: datetime | None = None,
) -> GlucoseLog:
    timestamp = taken_at or datetime.utcnow()
    log = GlucoseLog(
        patient_id=patient_id,
        value=value,
        type=type_value,
        taken_at=timestamp,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_by_patient(db: Session, patient_id: str) -> list[GlucoseLog]:
    return (
        db.query(GlucoseLog)
        .filter(GlucoseLog.patient_id == patient_id)
        .order_by(GlucoseLog.taken_at.desc(), GlucoseLog.created_at.desc())
        .all()
    )

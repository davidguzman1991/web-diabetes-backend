from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.patient import Patient


def normalize_password_seed(apellidos: str, nombres: str) -> str:
    return f"{apellidos}{nombres}".replace(" ", "").lower()


def get_by_cedula(db: Session, cedula: str) -> Patient | None:
    return db.query(Patient).filter(Patient.cedula == cedula).first()


def get_by_user_id(db: Session, user_id) -> Patient | None:
    return db.query(Patient).filter(Patient.user_id == user_id).first()


def get(db: Session, patient_id: str) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def list_patients(db: Session) -> list[Patient]:
    return db.query(Patient).order_by(Patient.apellidos.asc()).all()


def create(db: Session, data) -> Patient:
    seed = data.password or normalize_password_seed(data.apellidos, data.nombres)
    patient = Patient(
        cedula=data.cedula,
        apellidos=data.apellidos,
        nombres=data.nombres,
        fecha_nacimiento=data.fecha_nacimiento,
        email=data.email,
        activo=data.activo,
        password_hash=get_password_hash(seed),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def update(db: Session, patient: Patient, data) -> Patient:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


def deactivate(db: Session, patient: Patient) -> Patient:
    patient.activo = False
    db.commit()
    db.refresh(patient)
    return patient

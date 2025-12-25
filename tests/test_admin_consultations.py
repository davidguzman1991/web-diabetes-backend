import os
import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.dependencies import require_admin
from app.core.security import get_password_hash
from app.main import app
from app.models.consultation import Consultation
from app.models.consultation_medication import Medication
from app.models.patient import Patient


DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL, reason="DATABASE_URL not set for integration tests"
)


class DummyAdmin:
    id = "test-admin"
    username = "admin"
    role = "admin"
    activo = True


@pytest.fixture()
def client():
    app.dependency_overrides[require_admin] = lambda: DummyAdmin()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_patient(db) -> Patient:
    cedula = f"test-{uuid.uuid4().hex[:8]}"
    patient = Patient(
        cedula=cedula,
        apellidos="Test",
        nombres="User",
        fecha_nacimiento=date(1990, 1, 1),
        email=None,
        activo=True,
        password_hash=get_password_hash("testpass"),
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def _cleanup(db, patient_id: str) -> None:
    consultas = db.query(Consultation).filter(Consultation.patient_id == patient_id).all()
    consulta_ids = [c.id for c in consultas]
    if consulta_ids:
        db.query(Medication).filter(Medication.consultation_id.in_(consulta_ids)).delete(
            synchronize_session=False
        )
        db.query(Consultation).filter(Consultation.id.in_(consulta_ids)).delete(
            synchronize_session=False
        )
    db.query(Patient).filter(Patient.id == patient_id).delete(synchronize_session=False)
    db.commit()


def test_create_consultation_ok(client):
    db = SessionLocal()
    patient = None
    try:
        patient = _create_patient(db)
        payload = {
            "cedula": patient.cedula,
            "fecha": "2025-01-01",
            "diagnosis": "Diabetes tipo 2",
            "notes": "Notas",
            "indications": "Indicaciones",
            "medications": [
                {
                    "drug_name": "Metformina",
                    "dose": "500 mg",
                    "route": "VO",
                    "frequency": "Cada 12 h",
                    "duration": "30 dias",
                    "indications": "Con alimentos",
                    "sort_order": 0,
                }
            ],
        }
        res = client.post("/admin/consultations", json=payload)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["id"]
        assert data["medications"]
    finally:
        if patient:
            _cleanup(db, patient.id)
        db.close()


def test_create_consultation_patient_not_found(client):
    payload = {
        "cedula": "no-existe",
        "diagnosis": "Test",
        "medications": [{"drug_name": "Metformina"}],
    }
    res = client.post("/admin/consultations", json=payload)
    assert res.status_code == 404

from sqlalchemy.orm import Session

from app.models.visit import Visit
from app.models.prescription import PrescriptionItem


def list_by_patient(db: Session, patient_id: str) -> list[Visit]:
    return (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id)
        .order_by(Visit.fecha_consulta.desc())
        .all()
    )


def get(db: Session, visit_id: str) -> Visit | None:
    return db.query(Visit).filter(Visit.id == visit_id).first()


def create(db: Session, patient_id: str, data) -> Visit:
    visit = Visit(
        patient_id=patient_id,
        fecha_consulta=data.fecha_consulta,
        diagnostico=data.diagnostico,
        notas_medico=data.notas_medico,
    )
    db.add(visit)
    db.flush()

    for item in data.items:
        db.add(
            PrescriptionItem(
                visit_id=visit.id,
                medication_id=item.medication_id,
                medicamento_texto=item.medicamento_texto,
                dosis=item.dosis,
                horario=item.horario,
                via=item.via,
                duracion=item.duracion,
                instrucciones=item.instrucciones,
            )
        )

    db.commit()
    db.refresh(visit)
    return visit

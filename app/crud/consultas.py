from sqlalchemy.orm import Session

from app.models.consulta import Consulta
from app.models.medicamento import Medicamento


def list_by_patient_user(db: Session, patient_user_id: str) -> list[Consulta]:
    return (
        db.query(Consulta)
        .filter(Consulta.patient_user_id == patient_user_id)
        .order_by(Consulta.fecha.desc())
        .all()
    )


def get(db: Session, consulta_id: str) -> Consulta | None:
    return db.query(Consulta).filter(Consulta.id == consulta_id).first()


def get_latest_by_patient(db: Session, patient_user_id: str) -> Consulta | None:
    return (
        db.query(Consulta)
        .filter(Consulta.patient_user_id == patient_user_id)
        .order_by(Consulta.fecha.desc())
        .first()
    )


def create(db: Session, patient_user_id: str, admin_user_id: str, data) -> Consulta:
    consulta = Consulta(
        patient_user_id=patient_user_id,
        created_by_admin_id=admin_user_id,
        diagnostico=data.diagnostico,
        notas_medicas=data.notas_medicas,
        indicaciones_generales=data.indicaciones_generales,
    )
    db.add(consulta)
    db.flush()

    for item in data.medicamentos:
        db.add(
            Medicamento(
                consulta_id=consulta.id,
                nombre=item.nombre,
                dosis=item.dosis,
                horario=item.horario,
                via=item.via,
                duracion=item.duracion,
                notas=item.notas,
            )
        )

    db.commit()
    db.refresh(consulta)
    return consulta

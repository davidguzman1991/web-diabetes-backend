import uuid
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    diagnosis = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    indications = Column(Text, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    blood_pressure = Column(String(50), nullable=True)
    heart_rate = Column(Integer, nullable=True)
    oxygen_saturation = Column(Integer, nullable=True)
    abdominal_circumference = Column(Float, nullable=True)
    reason_for_visit = Column(String(255), nullable=True)
    current_illness = Column(Text, nullable=True)
    physical_exam = Column(Text, nullable=True)
    requested_exams = Column(Text, nullable=True)
    next_visit_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    consultation_date = Column(Date, nullable=True, index=True)

    patient = relationship("Patient", back_populates="consultations")
    medications = relationship(
        "Medication",
        back_populates="consultation",
        cascade="all, delete-orphan",
        order_by="Medication.sort_order",
    )
    labs = relationship("ConsultaLab", back_populates="consultation", cascade="all, delete-orphan")

    # Spanish aliases for legacy payloads/consumers without changing DB columns.
    @property
    def diagnostico(self) -> str | None:
        return self.diagnosis

    @diagnostico.setter
    def diagnostico(self, value: str | None) -> None:
        self.diagnosis = value

    @property
    def notas_medicas(self) -> str | None:
        return self.notes

    @notas_medicas.setter
    def notas_medicas(self, value: str | None) -> None:
        self.notes = value

    @property
    def notas(self) -> str | None:
        return self.notes

    @notas.setter
    def notas(self, value: str | None) -> None:
        self.notes = value

    @property
    def indicaciones(self) -> str | None:
        return self.indications

    @indicaciones.setter
    def indicaciones(self, value: str | None) -> None:
        self.indications = value

    @property
    def motivo_consulta(self) -> str | None:
        return self.reason_for_visit

    @motivo_consulta.setter
    def motivo_consulta(self, value: str | None) -> None:
        self.reason_for_visit = value

    @property
    def historia_actual(self) -> str | None:
        return self.current_illness

    @historia_actual.setter
    def historia_actual(self, value: str | None) -> None:
        self.current_illness = value

    @property
    def examen_fisico(self) -> str | None:
        return self.physical_exam

    @examen_fisico.setter
    def examen_fisico(self, value: str | None) -> None:
        self.physical_exam = value

    @property
    def examenes_solicitados(self) -> str | None:
        return self.requested_exams

    @examenes_solicitados.setter
    def examenes_solicitados(self, value: str | None) -> None:
        self.requested_exams = value

    @property
    def proxima_cita(self):
        return self.next_visit_date

    @proxima_cita.setter
    def proxima_cita(self, value) -> None:
        self.next_visit_date = value

    @property
    def signos_vitales(self) -> dict:
        return {
            "peso": self.weight,
            "talla": self.height,
            "presion_arterial": self.blood_pressure,
            "frecuencia_cardiaca": self.heart_rate,
            "saturacion_oxigeno": self.oxygen_saturation,
            "circunferencia_abdominal": self.abdominal_circumference,
        }

    @property
    def laboratorios(self) -> list[dict]:
        labs = self.labs or []
        payload = []
        for lab in labs:
            payload.append(
                {
                    "lab_id": str(lab.lab_id) if lab.lab_id else None,
                    "lab_nombre": getattr(lab.lab, "nombre", None) if lab.lab else None,
                    "valor_num": lab.valor_num,
                    "valor_texto": lab.valor_texto,
                    "unidad_snapshot": lab.unidad_snapshot,
                    "rango_ref_snapshot": lab.rango_ref_snapshot,
                }
            )
        return payload

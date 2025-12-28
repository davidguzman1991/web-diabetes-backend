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

    patient = relationship("Patient", back_populates="consultations")
    medications = relationship(
        "Medication",
        back_populates="consultation",
        cascade="all, delete-orphan",
        order_by="Medication.sort_order",
    )
    labs = relationship("ConsultaLab", back_populates="consultation", cascade="all, delete-orphan")

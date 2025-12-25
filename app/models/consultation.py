import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text
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
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    patient = relationship("Patient", back_populates="consultations")
    medications = relationship(
        "Medication",
        back_populates="consultation",
        cascade="all, delete-orphan",
        order_by="Medication.sort_order",
    )
    labs = relationship("ConsultaLab", back_populates="consultation", cascade="all, delete-orphan")

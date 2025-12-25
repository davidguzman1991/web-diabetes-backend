import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Consulta(Base):
    __tablename__ = "consultas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    diagnostico = Column(Text, nullable=True)
    notas_medicas = Column(Text, nullable=True)
    indicaciones_generales = Column(Text, nullable=True)
    created_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    medicamentos = relationship("Medicamento", back_populates="consulta", cascade="all, delete-orphan")

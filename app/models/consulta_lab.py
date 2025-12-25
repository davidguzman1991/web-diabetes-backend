import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ConsultaLab(Base):
    __tablename__ = "consulta_labs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_id = Column(UUID(as_uuid=True), ForeignKey("consultations.id"), nullable=False, index=True)
    lab_id = Column(UUID(as_uuid=True), ForeignKey("catalogo_labs.id"), nullable=False, index=True)
    valor_num = Column(Float, nullable=True)
    valor_texto = Column(Text, nullable=True)
    unidad_snapshot = Column(Text, nullable=True)
    rango_ref_snapshot = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    consultation = relationship("Consultation", back_populates="labs")
    lab = relationship("CatalogLab", back_populates="consulta_labs")

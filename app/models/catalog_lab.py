import uuid
from sqlalchemy import Boolean, Column, Float, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class CatalogLab(Base):
    __tablename__ = "catalogo_labs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(Text, nullable=False, unique=True, index=True)
    unidad = Column(Text, nullable=True)
    rango_ref_min = Column(Float, nullable=True)
    rango_ref_max = Column(Float, nullable=True)
    categoria = Column(Text, nullable=False, default="general", server_default=text("'general'"))
    orden = Column(Integer, nullable=False, default=0, server_default=text("0"))
    activo = Column(Boolean, default=True, nullable=False)

    consulta_labs = relationship("ConsultaLab", back_populates="lab")

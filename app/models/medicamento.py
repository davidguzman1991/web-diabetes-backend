import uuid
from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consulta_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nombre = Column(Text, nullable=False)
    dosis = Column(Text, nullable=False)
    horario = Column(Text, nullable=False)
    via = Column(Text, nullable=False)
    duracion = Column(Text, nullable=False)
    notas = Column(Text, nullable=True)

    consulta = relationship("Consulta", back_populates="medicamentos")

import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=False, index=True)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medication_catalog.id"), nullable=True, index=True)
    medicamento_texto = Column(String(255), nullable=True)
    dosis = Column(String(120), nullable=False)
    horario = Column(String(120), nullable=False)
    via = Column(String(120), nullable=False)
    duracion = Column(String(120), nullable=False)
    instrucciones = Column(Text, nullable=True)

    visit = relationship("Visit", back_populates="items")
    medication = relationship("MedicationCatalog")

    @property
    def medication_nombre(self) -> str | None:
        if self.medication:
            return self.medication.nombre_generico
        return None

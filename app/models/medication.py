import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import synonym

from app.core.database import Base


class MedicationCatalog(Base):
    __tablename__ = "medication_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_generico = Column(String(120), nullable=False, index=True)
    presentacion = Column(String(120), nullable=True)
    forma = Column(String(120), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    generic_name = synonym("nombre_generico")
    base_concentration = synonym("presentacion")
    form = synonym("forma")
    is_active = synonym("activo")

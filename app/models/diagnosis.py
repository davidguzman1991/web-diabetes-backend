import uuid
from sqlalchemy import Column, String, Boolean, text
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class DiagnosisCatalog(Base):
    __tablename__ = "diagnoses_catalog"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    cie10_code = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))

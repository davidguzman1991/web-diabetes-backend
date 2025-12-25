import uuid
from sqlalchemy import Column, String, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cedula = Column(String(50), unique=True, index=True, nullable=False)
    apellidos = Column(String(120), nullable=False)
    nombres = Column(String(120), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    email = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    consultations = relationship("Consultation", back_populates="patient", cascade="all, delete-orphan")
    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")

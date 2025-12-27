import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Medication(Base):
    __tablename__ = "medications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consultation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    drug_name = Column(Text, nullable=False)
    dose = Column(Text, nullable=True)
    route = Column(Text, nullable=True)
    frequency = Column(Text, nullable=True)
    duration = Column(Text, nullable=True)
    indications = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    consultation = relationship("Consultation", back_populates="medications")

    @staticmethod
    def _normalize_int(value) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        cleaned = str(value).strip()
        if not cleaned or not cleaned.isdigit():
            return None
        return int(cleaned)

    def _uses_legacy_fields(self) -> bool:
        if self.route or self.frequency:
            return True
        if self.dose and self._normalize_int(self.dose) is None:
            return True
        if self.duration and self._normalize_int(self.duration) is None:
            return True
        return False

    @property
    def quantity(self) -> int | None:
        return self._normalize_int(self.dose)

    @property
    def duration_days(self) -> int | None:
        return self._normalize_int(self.duration)

    @property
    def description(self) -> str | None:
        if not self._uses_legacy_fields():
            return self.indications or None
        parts: list[str] = []
        if self.dose:
            parts.append(f"Dosis: {self.dose}")
        if self.frequency:
            parts.append(f"Frecuencia: {self.frequency}")
        if self.route:
            parts.append(f"Via: {self.route}")
        if self.duration:
            parts.append(f"Duracion: {self.duration}")
        if self.indications:
            parts.append(f"Notas: {self.indications}")
        return " | ".join(parts) if parts else None

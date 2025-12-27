from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator, ConfigDict


class MedicationBase(BaseModel):
    drug_name: str
    dose: str | None = None
    route: str | None = None
    frequency: str | None = None
    duration: str | None = None
    indications: str | None = None
    sort_order: int | None = None

    @field_validator("drug_name")
    @classmethod
    def validate_drug_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("drug_name is required")
        return cleaned


class MedicationCreate(MedicationBase):
    @field_validator("dose")
    @classmethod
    def validate_dose(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("dose is required")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("dose is required")
        return cleaned


class MedicationUpdate(BaseModel):
    drug_name: str | None = None
    dose: str | None = None
    route: str | None = None
    frequency: str | None = None
    duration: str | None = None
    indications: str | None = None
    sort_order: int | None = None

    @field_validator("drug_name")
    @classmethod
    def validate_drug_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("drug_name is required")
        return cleaned


class MedicationOut(MedicationBase):
    id: UUID
    consultation_id: UUID
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

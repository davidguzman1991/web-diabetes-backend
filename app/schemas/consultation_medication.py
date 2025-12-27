from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator, ConfigDict


class MedicationBase(BaseModel):
    drug_name: str
    quantity: int | None = None
    description: str | None = None
    duration_days: int | None = None
    sort_order: int | None = None

    @field_validator("drug_name")
    @classmethod
    def validate_drug_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("drug_name is required")
        return cleaned


class MedicationCreate(MedicationBase):
    quantity: int

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("quantity", "duration_days")
    @classmethod
    def validate_positive_int(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("value must be positive")
        return value


class MedicationUpdate(BaseModel):
    drug_name: str | None = None
    quantity: int | None = None
    description: str | None = None
    duration_days: int | None = None
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

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("quantity", "duration_days")
    @classmethod
    def validate_positive_int(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("value must be positive")
        return value


class MedicationOut(MedicationBase):
    id: UUID
    consultation_id: UUID
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

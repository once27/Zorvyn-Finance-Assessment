from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.record import RecordType


class RecordCreate(BaseModel):
    amount: Decimal
    type: RecordType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class RecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[RecordType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class RecordRead(BaseModel):
    id: str
    user_id: str
    amount: Decimal
    type: RecordType
    category: str
    date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

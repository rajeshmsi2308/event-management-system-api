from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.models.enums import PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: int
    # Simulation: choose the result you want to test
    outcome: Literal["SUCCESS", "FAILED"] = "SUCCESS"


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_reference: str
    booking_id: int
    amount: Decimal
    status: PaymentStatus
    failure_reason: str | None
    created_at: datetime
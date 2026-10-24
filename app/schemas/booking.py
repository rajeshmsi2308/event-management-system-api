from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import BookingStatus


class BookingItemCreate(BaseModel):
    ticket_type_id: int
    quantity: int = Field(gt=0, le=10)  # max 10 per ticket type per booking


class BookingCreate(BaseModel):
    event_id: int
    items: list[BookingItemCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def no_duplicate_ticket_types(self):
        ids = [item.ticket_type_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("Each ticket type can appear only once in a booking")
        return self


class BookingItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_type_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_reference: str
    customer_id: int
    event_id: int
    total_amount: Decimal
    status: BookingStatus
    created_at: datetime
    cancelled_at: datetime | None
    items: list[BookingItemOut]
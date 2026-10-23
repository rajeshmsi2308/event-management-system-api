from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TicketTypeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)  # Regular / Standard / VIP
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    total_quantity: int = Field(gt=0)


class TicketTypeUpdate(BaseModel):
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    total_quantity: int | None = Field(default=None, gt=0)


class TicketTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    name: str
    price: Decimal
    total_quantity: int
    sold_quantity: int
    remaining_quantity: int
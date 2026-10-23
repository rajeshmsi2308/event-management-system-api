from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import EventStatus


def _naive(v: datetime | None) -> datetime | None:
    # MySQL DATETIME has no timezone, so we store plain local times.
    return v.replace(tzinfo=None) if v and v.tzinfo else v


class EventCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    category: str = Field(min_length=2, max_length=50)
    venue: str = Field(min_length=2, max_length=200)
    start_time: datetime
    end_time: datetime
    ticket_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    capacity: int = Field(gt=0)

    _strip_tz = field_validator("start_time", "end_time")(_naive)

    @model_validator(mode="after")
    def check_times(self):
        if self.start_time <= datetime.now():
            raise ValueError("start_time must be in the future")
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = None
    category: str | None = Field(default=None, min_length=2, max_length=50)
    venue: str | None = Field(default=None, min_length=2, max_length=200)
    start_time: datetime | None = None
    end_time: datetime | None = None
    ticket_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    capacity: int | None = Field(default=None, gt=0)

    _strip_tz = field_validator("start_time", "end_time")(_naive)


class EventStatusUpdate(BaseModel):
    status: EventStatus


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    category: str
    venue: str
    start_time: datetime
    end_time: datetime
    ticket_price: Decimal
    capacity: int
    status: EventStatus
    organizer_id: int
    created_at: datetime
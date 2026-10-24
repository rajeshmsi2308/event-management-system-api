import math
from datetime import date, datetime, time
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models import Event, EventStatus, User, UserRole
from app.schemas.event import EventCreate, EventUpdate

# Which status changes are allowed
ALLOWED_TRANSITIONS = {
    EventStatus.DRAFT: {EventStatus.PUBLISHED, EventStatus.CANCELLED},
    EventStatus.PUBLISHED: {EventStatus.CANCELLED, EventStatus.COMPLETED},
    EventStatus.CANCELLED: set(),
    EventStatus.COMPLETED: set(),
}

# Columns the user is allowed to sort by
SORT_COLUMNS = {
    "start_time": Event.start_time,
    "ticket_price": Event.ticket_price,
    "title": Event.title,
    "created_at": Event.created_at,
}


def get_event_or_404(db: Session, event_id: int) -> Event:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


def ensure_can_manage(event: Event, user: User) -> None:
    if user.role != UserRole.ADMIN and event.organizer_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only manage your own events")


def create_event(db: Session, data: EventCreate, organizer: User) -> Event:
    event = Event(**data.model_dump(), organizer_id=organizer.id, status=EventStatus.DRAFT)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def search_events(
    db: Session,
    q: str | None = None,
    category: str | None = None,
    venue: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    sort_by: str = "start_time",
    order: str = "asc",
    page: int = 1,
    size: int = 10,
) -> dict:
    """Public search: only PUBLISHED events."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "start_date cannot be after end_date")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "min_price cannot be more than max_price")

    filters = [Event.status == EventStatus.PUBLISHED]
    if q:
        like = f"%{q.strip()}%"
        filters.append(or_(Event.title.ilike(like), Event.description.ilike(like), Event.venue.ilike(like)))
    if category:
        filters.append(Event.category == category.strip())
    if venue:
        filters.append(Event.venue.ilike(f"%{venue.strip()}%"))
    if start_date:
        filters.append(Event.start_time >= datetime.combine(start_date, time.min))
    if end_date:
        filters.append(Event.start_time <= datetime.combine(end_date, time.max))
    if min_price is not None:
        filters.append(Event.ticket_price >= min_price)
    if max_price is not None:
        filters.append(Event.ticket_price <= max_price)

    total = db.scalar(select(func.count(Event.id)).where(*filters))

    column = SORT_COLUMNS[sort_by]
    ordering = column.desc() if order == "desc" else column.asc()
    stmt = (
        select(Event)
        .where(*filters)
        .order_by(ordering, Event.id)
        .offset((page - 1) * size)
        .limit(size)
    )
    items = list(db.scalars(stmt))

    return {"items": items, "total": total, "page": page, "size": size, "pages": math.ceil(total / size) if total else 0}


def list_my_events(db: Session, user: User) -> list[Event]:
    stmt = select(Event).order_by(Event.created_at.desc())
    if user.role != UserRole.ADMIN:
        stmt = stmt.where(Event.organizer_id == user.id)
    return list(db.scalars(stmt))


def update_event(db: Session, event: Event, data: EventUpdate) -> Event:
    if event.status in (EventStatus.CANCELLED, EventStatus.COMPLETED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot edit a {event.status.value} event")

    changes = data.model_dump(exclude_unset=True)
    start = changes.get("start_time", event.start_time)
    end = changes.get("end_time", event.end_time)
    if "start_time" in changes and start <= datetime.now():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "start_time must be in the future")
    if end <= start:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "end_time must be after start_time")

    for field, value in changes.items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def change_status(db: Session, event: Event, new_status: EventStatus) -> Event:
    if new_status not in ALLOWED_TRANSITIONS[event.status]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Cannot change status from {event.status.value} to {new_status.value}",
        )
    try:
        if new_status == EventStatus.CANCELLED:
            # Imported here to avoid a circular import (booking_service imports this file)
            from app.services.booking_service import cancel_event_bookings
            cancel_event_bookings(db, event)
        event.status = new_status
        db.commit()  # status change + all cancellations/refunds saved together
    except Exception:
        db.rollback()
        raise

    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    if event.status != EventStatus.DRAFT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only DRAFT events can be deleted. Cancel it instead.")
    db.delete(event)
    db.commit()
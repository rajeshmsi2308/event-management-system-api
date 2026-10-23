from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
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


def list_published_events(db: Session) -> list[Event]:
    stmt = select(Event).where(Event.status == EventStatus.PUBLISHED).order_by(Event.start_time)
    return list(db.scalars(stmt))


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
    event.status = new_status
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    if event.status != EventStatus.DRAFT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only DRAFT events can be deleted. Cancel it instead.")
    db.delete(event)
    db.commit()
from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Form, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_roles
from app.models import EventStatus, User, UserRole
from app.models.enums import EventCategory
from app.schemas.common import Page
from app.schemas.event import EventCreate, EventUpdate, EventStatusUpdate, EventOut
from app.services import event_service

router = APIRouter(prefix="/api/events", tags=["Events"])

organizer_or_admin = require_roles(UserRole.ORGANIZER, UserRole.ADMIN)


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(data: Annotated[EventCreate, Form()], db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    return event_service.create_event(db, data, user)


@router.get("", response_model=Page[EventOut])
def search_events(
    q: str | None = Query(None, description="Keyword in title, description or venue"),
    category: EventCategory | None = Query(None, description="Pick a category"),
    venue: str | None = None,
    start_date: date | None = Query(None, description="Events starting on or after (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Events starting on or before (YYYY-MM-DD)"),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    sort_by: Literal["start_time", "ticket_price", "title", "created_at"] = "start_time",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Public: search, filter, sort and paginate PUBLISHED events."""
    return event_service.search_events(
        db, q, category.value if category else None, venue, start_date, end_date, min_price, max_price, sort_by, order, page, size
    )


@router.get("/mine", response_model=list[EventOut])
def my_events(db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    """Organizer: own events in every status. Admin: all events."""
    return event_service.list_my_events(db, user)


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = event_service.get_event_or_404(db, event_id)
    if event.status == EventStatus.DRAFT:
        # Drafts are private; organizers see them via /mine
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


@router.patch("/{event_id}", response_model=EventOut)
def update_event(event_id: int, data: Annotated[EventUpdate, Form()], db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    return event_service.update_event(db, event, data)


@router.patch("/{event_id}/status", response_model=EventOut)
def update_status(event_id: int, data: Annotated[EventStatusUpdate, Form()], db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    return event_service.change_status(db, event, data.status)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    event_service.delete_event(db, event)

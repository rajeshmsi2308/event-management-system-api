from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_roles
from app.models import EventStatus, User, UserRole
from app.schemas.event import EventCreate, EventUpdate, EventStatusUpdate, EventOut
from app.services import event_service

router = APIRouter(prefix="/api/events", tags=["Events"])

organizer_or_admin = require_roles(UserRole.ORGANIZER, UserRole.ADMIN)


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(data: EventCreate, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    return event_service.create_event(db, data, user)


@router.get("", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    """Public: only PUBLISHED events."""
    return event_service.list_published_events(db)


@router.get("/mine", response_model=list[EventOut])
def my_events(db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    """Organizer: own events in every status. Admin: all events."""
    return event_service.list_my_events(db, user)


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = event_service.get_event_or_404(db, event_id)
    if event.status == EventStatus.DRAFT:
        # Drafts are private; organizers see them via /mine
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return event


@router.patch("/{event_id}", response_model=EventOut)
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    return event_service.update_event(db, event, data)


@router.patch("/{event_id}/status", response_model=EventOut)
def update_status(event_id: int, data: EventStatusUpdate, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    return event_service.change_status(db, event, data.status)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    event_service.delete_event(db, event)
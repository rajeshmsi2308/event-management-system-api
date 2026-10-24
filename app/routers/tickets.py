from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_roles
from app.models import User, UserRole
from app.schemas.ticket import TicketTypeCreate, TicketTypeUpdate, TicketTypeOut
from app.services import ticket_service

router = APIRouter(prefix="/api", tags=["Tickets"])

organizer_or_admin = require_roles(UserRole.ORGANIZER, UserRole.ADMIN)


@router.post("/events/{event_id}/ticket-types", response_model=TicketTypeOut, status_code=status.HTTP_201_CREATED)
def create_ticket_type(event_id: int, data: Annotated[TicketTypeCreate, Form()], db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    return ticket_service.create_ticket_type(db, event_id, data, user)


@router.get("/events/{event_id}/ticket-types", response_model=list[TicketTypeOut])
def list_ticket_types(event_id: int, db: Session = Depends(get_db)):
    """Public: ticket types of a published event."""
    return ticket_service.list_ticket_types(db, event_id)


@router.patch("/ticket-types/{ticket_type_id}", response_model=TicketTypeOut)
def update_ticket_type(ticket_type_id: int, data: Annotated[TicketTypeUpdate, Form()], db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    ticket_type = ticket_service.get_ticket_type_or_404(db, ticket_type_id)
    return ticket_service.update_ticket_type(db, ticket_type, data, user)


@router.delete("/ticket-types/{ticket_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_type(ticket_type_id: int, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    ticket_type = ticket_service.get_ticket_type_or_404(db, ticket_type_id)
    ticket_service.delete_ticket_type(db, ticket_type, user)

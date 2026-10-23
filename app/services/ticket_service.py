from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Event, EventStatus, TicketType, User
from app.schemas.ticket import TicketTypeCreate, TicketTypeUpdate
from app.services.event_service import get_event_or_404, ensure_can_manage


def get_ticket_type_or_404(db: Session, ticket_type_id: int) -> TicketType:
    ticket_type = db.get(TicketType, ticket_type_id)
    if not ticket_type:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket type not found")
    return ticket_type


def _ensure_event_open(event: Event) -> None:
    if event.status in (EventStatus.CANCELLED, EventStatus.COMPLETED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Cannot change tickets of a {event.status.value} event")


def _allocated_quantity(db: Session, event_id: int, exclude_id: int | None = None) -> int:
    """Sum of total_quantity of all ticket types of an event."""
    stmt = select(func.coalesce(func.sum(TicketType.total_quantity), 0)).where(TicketType.event_id == event_id)
    if exclude_id:
        stmt = stmt.where(TicketType.id != exclude_id)
    return db.scalar(stmt)


def _ensure_capacity(db: Session, event: Event, new_quantity: int, exclude_id: int | None = None) -> None:
    used = _allocated_quantity(db, event.id, exclude_id)
    if used + new_quantity > event.capacity:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Exceeds event capacity ({event.capacity}). Already allocated: {used}",
        )


def create_ticket_type(db: Session, event_id: int, data: TicketTypeCreate, user: User) -> TicketType:
    event = get_event_or_404(db, event_id)
    ensure_can_manage(event, user)
    _ensure_event_open(event)

    duplicate = db.scalar(
        select(TicketType).where(TicketType.event_id == event_id, TicketType.name == data.name.strip())
    )
    if duplicate:
        raise HTTPException(status.HTTP_409_CONFLICT, "This event already has a ticket type with that name")

    _ensure_capacity(db, event, data.total_quantity)

    ticket_type = TicketType(
        event_id=event_id,
        name=data.name.strip(),
        price=data.price,
        total_quantity=data.total_quantity,
        sold_quantity=0,
    )
    db.add(ticket_type)
    db.commit()
    db.refresh(ticket_type)
    return ticket_type


def list_ticket_types(db: Session, event_id: int) -> list[TicketType]:
    event = get_event_or_404(db, event_id)
    if event.status == EventStatus.DRAFT:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return list(db.scalars(select(TicketType).where(TicketType.event_id == event_id).order_by(TicketType.price)))


def update_ticket_type(db: Session, ticket_type: TicketType, data: TicketTypeUpdate, user: User) -> TicketType:
    event = ticket_type.event
    ensure_can_manage(event, user)
    _ensure_event_open(event)

    if data.total_quantity is not None:
        if data.total_quantity < ticket_type.sold_quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Quantity cannot be less than tickets already sold ({ticket_type.sold_quantity})",
            )
        _ensure_capacity(db, event, data.total_quantity, exclude_id=ticket_type.id)
        ticket_type.total_quantity = data.total_quantity

    if data.price is not None:
        ticket_type.price = data.price

    db.commit()
    db.refresh(ticket_type)
    return ticket_type


def delete_ticket_type(db: Session, ticket_type: TicketType, user: User) -> None:
    ensure_can_manage(ticket_type.event, user)
    if ticket_type.sold_quantity > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot delete a ticket type that has sales")
    db.delete(ticket_type)
    db.commit()
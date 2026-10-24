import secrets
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, BookingItem, EventStatus, TicketType, User, UserRole
from app.schemas.booking import BookingCreate
from app.services.event_service import get_event_or_404


def _generate_reference(db: Session) -> str:
    """e.g. EVT-20261024-A1B2C3, retried until unique."""
    while True:
        ref = f"EVT-{datetime.now():%Y%m%d}-{secrets.token_hex(3).upper()}"
        if not db.scalar(select(Booking.id).where(Booking.booking_reference == ref)):
            return ref


def create_booking(db: Session, data: BookingCreate, customer: User) -> Booking:
    event = get_event_or_404(db, data.event_id)
    if event.status != EventStatus.PUBLISHED:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bookings are open only for published events")
    if event.start_time <= datetime.now():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This event has already started")

    try:
        # Lock the requested ticket rows until commit (prevents overselling).
        # Sorted by id so two bookings always lock in the same order (no deadlocks).
        requested_ids = sorted(item.ticket_type_id for item in data.items)
        ticket_types = db.scalars(
            select(TicketType).where(TicketType.id.in_(requested_ids)).order_by(TicketType.id).with_for_update()
        ).all()
        ticket_map = {t.id: t for t in ticket_types}

        booking = Booking(
            booking_reference=_generate_reference(db),
            customer_id=customer.id,
            event_id=event.id,
            total_amount=Decimal("0.00"),
        )
        total = Decimal("0.00")

        for item in data.items:
            ticket = ticket_map.get(item.ticket_type_id)
            if ticket is None or ticket.event_id != event.id:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Ticket type {item.ticket_type_id} does not belong to this event")
            if item.quantity > ticket.remaining_quantity:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    f"Only {ticket.remaining_quantity} {ticket.name} ticket(s) left",
                )

            subtotal = ticket.price * item.quantity
            total += subtotal
            ticket.sold_quantity += item.quantity  # reserve seats
            booking.items.append(
                BookingItem(ticket_type_id=ticket.id, quantity=item.quantity, unit_price=ticket.price, subtotal=subtotal)
            )

        booking.total_amount = total
        db.add(booking)
        db.commit()  # everything saved together, locks released
    except Exception:
        db.rollback()  # nothing is saved if any check fails
        raise

    db.refresh(booking)
    return booking


def get_booking_or_404(db: Session, booking_id: int) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    return booking


def ensure_can_view(booking: Booking, user: User) -> None:
    if user.role != UserRole.ADMIN and booking.customer_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own bookings")


def list_my_bookings(db: Session, user: User) -> list[Booking]:
    stmt = select(Booking).where(Booking.customer_id == user.id).order_by(Booking.created_at.desc())
    return list(db.scalars(stmt))
import math
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import (
    Booking, BookingItem, BookingStatus, Event, EventStatus, Payment, PaymentStatus,
    TicketType, User, UserRole,
)


def _count_by(db: Session, column, enum_cls, *filters) -> dict[str, int]:
    """Counts rows grouped by an enum column, showing 0 for missing values."""
    result = {member.value: 0 for member in enum_cls}
    rows = db.execute(select(column, func.count()).where(*filters).group_by(column)).all()
    for value, count in rows:
        result[value.value] = count
    return result


def _sum_payments(db: Session, payment_status: PaymentStatus, event_id: int | None = None) -> Decimal:
    stmt = select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == payment_status)
    if event_id is not None:
        stmt = stmt.join(Booking, Booking.id == Payment.booking_id).where(Booking.event_id == event_id)
    return Decimal(db.scalar(stmt))


def get_dashboard(db: Session) -> dict:
    tickets_sold = db.scalar(
        select(func.coalesce(func.sum(BookingItem.quantity), 0))
        .join(Booking, Booking.id == BookingItem.booking_id)
        .where(Booking.status == BookingStatus.CONFIRMED)
    )

    revenue = func.coalesce(func.sum(Booking.total_amount), 0).label("revenue")
    top_rows = db.execute(
        select(Event.id, Event.title, func.count(Booking.id), revenue)
        .join(Booking, Booking.event_id == Event.id)
        .where(Booking.status == BookingStatus.CONFIRMED)
        .group_by(Event.id, Event.title)
        .order_by(revenue.desc())
        .limit(5)
    ).all()

    return {
        "users_by_role": _count_by(db, User.role, UserRole),
        "events_by_status": _count_by(db, Event.status, EventStatus),
        "bookings_by_status": _count_by(db, Booking.status, BookingStatus),
        "total_revenue": _sum_payments(db, PaymentStatus.SUCCESS),
        "total_refunded": _sum_payments(db, PaymentStatus.REFUNDED),
        "tickets_sold": int(tickets_sold),
        "top_events": [
            {"event_id": r[0], "title": r[1], "confirmed_bookings": r[2], "revenue": Decimal(r[3])}
            for r in top_rows
        ],
    }


def get_event_sales_report(db: Session, event: Event) -> dict:
    # Paid quantity and revenue per ticket type (CONFIRMED bookings only)
    confirmed_rows = db.execute(
        select(
            BookingItem.ticket_type_id,
            func.coalesce(func.sum(BookingItem.quantity), 0),
            func.coalesce(func.sum(BookingItem.subtotal), 0),
        )
        .join(Booking, Booking.id == BookingItem.booking_id)
        .where(Booking.event_id == event.id, Booking.status == BookingStatus.CONFIRMED)
        .group_by(BookingItem.ticket_type_id)
    ).all()
    confirmed = {row[0]: (int(row[1]), Decimal(row[2])) for row in confirmed_rows}

    ticket_types = db.scalars(select(TicketType).where(TicketType.event_id == event.id).order_by(TicketType.id)).all()
    ticket_sales = []
    total_qty, total_revenue = 0, Decimal("0.00")
    for t in ticket_types:
        qty, rev = confirmed.get(t.id, (0, Decimal("0.00")))
        total_qty += qty
        total_revenue += rev
        ticket_sales.append({
            "ticket_type_id": t.id,
            "name": t.name,
            "price": t.price,
            "total_quantity": t.total_quantity,
            "reserved_or_sold": t.sold_quantity,
            "confirmed_quantity": qty,
            "remaining_quantity": t.remaining_quantity,
            "revenue": rev,
        })

    return {
        "event_id": event.id,
        "title": event.title,
        "status": event.status.value,
        "capacity": event.capacity,
        "bookings_by_status": _count_by(db, Booking.status, BookingStatus, Booking.event_id == event.id),
        "ticket_types": ticket_sales,
        "total_tickets_confirmed": total_qty,
        "total_revenue": total_revenue,
        "total_refunded": _sum_payments(db, PaymentStatus.REFUNDED, event.id),
    }


def list_users(db: Session, role: UserRole | None, page: int, size: int) -> dict:
    filters = [User.role == role] if role else []
    total = db.scalar(select(func.count(User.id)).where(*filters))
    items = list(db.scalars(
        select(User).where(*filters).order_by(User.id).offset((page - 1) * size).limit(size)
    ))
    return {"items": items, "total": total, "page": page, "size": size, "pages": math.ceil(total / size) if total else 0}
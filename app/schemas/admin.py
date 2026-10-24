from decimal import Decimal

from pydantic import BaseModel


class TopEvent(BaseModel):
    event_id: int
    title: str
    confirmed_bookings: int
    revenue: Decimal


class DashboardOut(BaseModel):
    users_by_role: dict[str, int]
    events_by_status: dict[str, int]
    bookings_by_status: dict[str, int]
    total_revenue: Decimal
    total_refunded: Decimal
    tickets_sold: int
    top_events: list[TopEvent]


class TicketTypeSales(BaseModel):
    ticket_type_id: int
    name: str
    price: Decimal
    total_quantity: int
    reserved_or_sold: int      # includes PENDING bookings holding seats
    confirmed_quantity: int    # paid tickets only
    remaining_quantity: int
    revenue: Decimal


class EventSalesReport(BaseModel):
    event_id: int
    title: str
    status: str
    capacity: int
    bookings_by_status: dict[str, int]
    ticket_types: list[TicketTypeSales]
    total_tickets_confirmed: int
    total_revenue: Decimal
    total_refunded: Decimal
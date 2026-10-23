from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TicketType(Base):
    __tablename__ = "ticket_types"
    __table_args__ = (
        UniqueConstraint("event_id", "name", name="uq_ticket_type_event_name"),
        CheckConstraint("price >= 0", name="ck_ticket_price_non_negative"),
        CheckConstraint("total_quantity > 0", name="ck_ticket_total_positive"),
        CheckConstraint("sold_quantity >= 0 AND sold_quantity <= total_quantity", name="ck_ticket_sold_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # Regular / Standard / VIP
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    event = relationship("Event", back_populates="ticket_types")
    booking_items = relationship("BookingItem", back_populates="ticket_type")

    @property
    def remaining_quantity(self) -> int:
        return self.total_quantity - self.sold_quantity
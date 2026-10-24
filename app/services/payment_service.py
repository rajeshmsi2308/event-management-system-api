import secrets

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, BookingStatus, Payment, PaymentStatus, User, UserRole
from app.schemas.payment import PaymentCreate
from app.services.notification_service import notify


def _generate_txn_reference(db: Session) -> str:
    """e.g. TXN-9F3A1C7B2E4D, retried until unique."""
    while True:
        ref = f"TXN-{secrets.token_hex(6).upper()}"
        if not db.scalar(select(Payment.id).where(Payment.transaction_reference == ref)):
            return ref


def process_payment(db: Session, data: PaymentCreate, user: User) -> Payment:
    try:
        # Lock the booking row: a second payment request for the same booking waits here,
        # then sees CONFIRMED and is rejected (no duplicate processing).
        booking = db.scalar(select(Booking).where(Booking.id == data.booking_id).with_for_update())
        if not booking:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
        if booking.customer_id != user.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only pay for your own bookings")
        if booking.status == BookingStatus.CONFIRMED:
            raise HTTPException(status.HTTP_409_CONFLICT, "This booking is already paid")
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot pay for a cancelled booking")

        payment = Payment(
            transaction_reference=_generate_txn_reference(db),
            booking_id=booking.id,
            amount=booking.total_amount,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)

        if data.outcome == "SUCCESS":
            payment.status = PaymentStatus.SUCCESS
            booking.status = BookingStatus.CONFIRMED
            notify(db, user.id, "Payment successful",
                   f"Payment of Rs.{booking.total_amount} for booking {booking.booking_reference} succeeded. Your booking is confirmed.")
        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = "Simulated payment failure"
            # Booking stays PENDING so the customer can retry
            notify(db, user.id, "Payment failed",
                   f"Payment for booking {booking.booking_reference} failed. You can try again.")

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(payment)
    return payment


def list_booking_payments(db: Session, booking_id: int, user: User) -> list[Payment]:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    if user.role != UserRole.ADMIN and booking.customer_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own payments")
    return list(db.scalars(select(Payment).where(Payment.booking_id == booking_id).order_by(Payment.id)))
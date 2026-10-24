from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import User, UserRole
from app.schemas.booking import BookingForm, BookingOut
from app.services import booking_service

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(data: Annotated[BookingForm, Form()], db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    return booking_service.create_booking(db, data.to_booking_create(), user)


@router.get("/me", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return booking_service.list_my_bookings(db, user)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = booking_service.get_booking_or_404(db, booking_id)
    booking_service.ensure_can_view(booking, user)
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Customer cancels own booking; Admin can cancel any."""
    return booking_service.cancel_booking(db, booking_id, user)

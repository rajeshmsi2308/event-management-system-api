from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models import User, UserRole
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services import payment_service

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def make_payment(data: PaymentCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.CUSTOMER))):
    return payment_service.process_payment(db, data, user)


@router.get("/booking/{booking_id}", response_model=list[PaymentOut])
def booking_payments(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return payment_service.list_booking_payments(db, booking_id, user)
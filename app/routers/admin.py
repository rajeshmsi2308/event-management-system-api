from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_roles
from app.models import User, UserRole
from app.schemas.admin import DashboardOut, EventSalesReport
from app.schemas.common import Page
from app.schemas.user import UserOut
from app.services import admin_service, event_service

router = APIRouter(prefix="/api/admin", tags=["Admin"])

admin_only = require_roles(UserRole.ADMIN)
organizer_or_admin = require_roles(UserRole.ORGANIZER, UserRole.ADMIN)


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db), user: User = Depends(admin_only)):
    return admin_service.get_dashboard(db)


@router.get("/events/{event_id}/sales-report", response_model=EventSalesReport)
def event_sales_report(event_id: int, db: Session = Depends(get_db), user: User = Depends(organizer_or_admin)):
    """Admin: any event. Organizer: own events only."""
    event = event_service.get_event_or_404(db, event_id)
    event_service.ensure_can_manage(event, user)
    return admin_service.get_event_sales_report(db, event)


@router.get("/users", response_model=Page[UserOut])
def list_users(
    role: UserRole | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(admin_only),
):
    return admin_service.list_users(db, role, page, size)
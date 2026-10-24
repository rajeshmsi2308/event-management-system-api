from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.notification import NotificationOut, UnreadCount
from app.services import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/me", response_model=list[NotificationOut])
def my_notifications(unread_only: bool = False, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return notification_service.list_my_notifications(db, user, unread_only)


@router.get("/me/unread-count", response_model=UnreadCount)
def my_unread_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return UnreadCount(unread=notification_service.unread_count(db, user))


@router.patch("/read-all")
def read_all(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    notification_service.mark_all_as_read(db, user)
    return {"message": "All notifications marked as read"}


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def read_one(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return notification_service.mark_as_read(db, notification_id, user)
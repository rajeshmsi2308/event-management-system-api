from fastapi import HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session

from app.models import Notification, User


def notify(db: Session, user_id: int, title: str, message: str) -> None:
    """Adds a notification. The caller commits, so it saves together with the main action."""
    db.add(Notification(user_id=user_id, title=title, message=message))


def list_my_notifications(db: Session, user: User, unread_only: bool = False) -> list[Notification]:
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    return list(db.scalars(stmt.order_by(Notification.created_at.desc(), Notification.id.desc())))


def unread_count(db: Session, user: User) -> int:
    return db.scalar(
        select(func.count(Notification.id)).where(Notification.user_id == user.id, Notification.is_read.is_(False))
    )


def mark_as_read(db: Session, notification_id: int, user: User) -> Notification:
    notification = db.get(Notification, notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user: User) -> None:
    db.execute(
        update(Notification).where(Notification.user_id == user.id, Notification.is_read.is_(False)).values(is_read=True)
    )
    db.commit()
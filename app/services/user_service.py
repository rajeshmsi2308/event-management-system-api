from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.schemas.user import UserRegister, UserUpdate, ChangePassword
from app.utils.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def register_user(db: Session, data: UserRegister) -> User:
    if get_user_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered")

    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        role=UserRole(data.role.value),  # SignupRole -> UserRole (never ADMIN)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is disabled")
    return user


def update_profile(db: Session, user: User, data: UserUpdate) -> User:
    if data.email and data.email.lower() != user.email:
        if get_user_by_email(db, data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email is already registered")
        user.email = data.email.lower()
    if data.name:
        user.name = data.name.strip()
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, data: ChangePassword) -> None:
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    if data.current_password == data.new_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "New password must be different")
    user.hashed_password = hash_password(data.new_password)
    db.commit()

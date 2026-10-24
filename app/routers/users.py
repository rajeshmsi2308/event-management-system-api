from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.user import UserOut, UserUpdate, ChangePassword
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(data: Annotated[UserUpdate, Form()], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_service.update_profile(db, current_user, data)


@router.post("/me/change-password")
def change_my_password(data: Annotated[ChangePassword, Form()], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_service.change_password(db, current_user, data)
    return {"message": "Password changed successfully"}

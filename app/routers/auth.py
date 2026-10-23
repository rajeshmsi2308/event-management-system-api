from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token
from app.schemas.user import UserRegister, UserOut
from app.services import user_service
from app.utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    return user_service.register_user(db, data)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger's "Authorize" button sends the email in the `username` field.
    user = user_service.authenticate_user(db, form.username, form.password)
    return Token(access_token=create_access_token(user.id, user.role.value))
"""Run once to create the admin users:  python create_admin.py"""
from app.database import SessionLocal, Base, engine
from app import models  # noqa: F401
from app.models import User, UserRole
from app.utils.security import hash_password

ADMINS = [
    ("Admin", "admin@gmail.com"),
    ("Admin One", "admin1@gmail.com"),
]
PASSWORD = "admin123"

# This line creates all 7 tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()
for name, email in ADMINS:
    if db.query(User).filter(User.email == email).first():
        print(f"Admin already exists: {email}")
    else:
        db.add(User(name=name, email=email, hashed_password=hash_password(PASSWORD), role=UserRole.ADMIN))
        db.commit()
        print(f"Admin created: {email} / {PASSWORD}")
db.close()

"""Run once to create an admin user:  python create_admin.py"""
from app.database import SessionLocal
from app.models import User, UserRole
from app.utils.security import hash_password

db = SessionLocal()
email = "admin@events.com"
if db.query(User).filter(User.email == email).first():
    print("Admin already exists")
else:
    db.add(User(name="Admin", email=email, hashed_password=hash_password("Admin@123"), role=UserRole.ADMIN))
    db.commit()
    print(f"Admin created: {email} / Admin@123")
db.close()
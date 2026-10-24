from fastapi import FastAPI

from app.database import Base, engine
from app import models  # noqa: F401  (registers all tables with Base)
from app.routers import auth, users, events, tickets, bookings, payments, notifications, admin

app = FastAPI(
    title="Event Management System API",
    description="Register, browse events, book tickets, simulate payments and manage bookings.",
    version="1.0.0",
)

# Creates any missing tables on startup (existing ones are untouched).
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(notifications.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Event Management System API is running", "docs": "/docs"}
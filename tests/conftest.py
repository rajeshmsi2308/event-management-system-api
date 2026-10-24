import os

# Tests use a separate SQLite file, so your real MySQL data is never touched.
# These must be set BEFORE the app is imported.
os.environ["DATABASE_URL"] = "sqlite:///./test_events.db"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import User, UserRole
from app.utils.security import hash_password


@pytest.fixture()
def client():
    # Fresh, empty tables for every test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


# ---------- helpers used by the tests ----------

def register(client, email, role="CUSTOMER", password="pass12345", name="Test User"):
    return client.post("/api/auth/register", data={"name": name, "email": email, "password": password, "role": role})


def login(client, email, password="pass12345"):
    res = client.post("/api/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def create_admin(email="admin@test.com", password="pass12345"):
    db = SessionLocal()
    db.add(User(name="Admin", email=email, hashed_password=hash_password(password), role=UserRole.ADMIN))
    db.commit()
    db.close()


def event_payload(**overrides):
    data = {
        "title": "Tech Meetup",
        "description": "Python talks",
        "category": "Technology",
        "venue": "Hitex, Hyderabad",
        "start_time": "2030-12-05T18:00:00",
        "end_time": "2030-12-05T21:00:00",
        "ticket_price": 499.00,
        "capacity": 100,
    }
    data.update(overrides)
    return data


def published_event_with_tickets(client, organizer_headers, regular_qty=5, **event_overrides):
    """Creates a published event with one 'Regular' ticket type. Returns (event_id, ticket_type_id)."""
    event = client.post("/api/events", data=event_payload(**event_overrides), headers=organizer_headers).json()
    ticket = client.post(
        f"/api/events/{event['id']}/ticket-types",
        data={"name": "Regular", "price": 499.00, "total_quantity": regular_qty},
        headers=organizer_headers,
    ).json()
    client.patch(f"/api/events/{event['id']}/status", data={"status": "PUBLISHED"}, headers=organizer_headers)
    return event["id"], ticket["id"]

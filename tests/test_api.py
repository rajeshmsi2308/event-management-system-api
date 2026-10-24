"""The 12 test scenarios required by the task brief."""
from tests.conftest import (
    register, login, create_admin, event_payload, published_event_with_tickets,
)


def _organizer_and_customer(client):
    register(client, "org@test.com", role="ORGANIZER")
    register(client, "cust@test.com")
    return login(client, "org@test.com"), login(client, "cust@test.com")


# 1
def test_register_new_email_succeeds(client):
    res = register(client, "new@test.com")
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "new@test.com"
    assert body["role"] == "CUSTOMER"
    assert "password" not in body and "hashed_password" not in body


# 2
def test_register_existing_email_rejected(client):
    register(client, "dup@test.com")
    res = register(client, "dup@test.com")
    assert res.status_code == 409


# 3
def test_login_wrong_password_rejected(client):
    register(client, "user@test.com")
    res = client.post("/api/auth/login", data={"username": "user@test.com", "password": "wrongpass"})
    assert res.status_code == 401


# 4
def test_create_event_without_auth_rejected(client):
    res = client.post("/api/events", data=event_payload())
    assert res.status_code == 401


# 5
def test_customer_cannot_create_event(client):
    register(client, "cust@test.com")
    res = client.post("/api/events", data=event_payload(), headers=login(client, "cust@test.com"))
    assert res.status_code == 403


# 6
def test_book_within_availability_succeeds(client):
    org, cust = _organizer_and_customer(client)
    event_id, ticket_id = published_event_with_tickets(client, org, regular_qty=5)

    res = client.post("/api/bookings", data={"event_id": event_id, "ticket_type_id": ticket_id, "quantity": 2}, headers=cust)
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "PENDING"
    assert body["booking_reference"].startswith("EVT-")
    assert float(body["total_amount"]) == 998.00  # 2 x 499, calculated by backend

    tickets = client.get(f"/api/events/{event_id}/ticket-types").json()
    assert tickets[0]["remaining_quantity"] == 3


# 7
def test_book_more_than_available_rejected(client):
    org, cust = _organizer_and_customer(client)
    event_id, ticket_id = published_event_with_tickets(client, org, regular_qty=3)

    res = client.post("/api/bookings", data={"event_id": event_id, "ticket_type_id": ticket_id, "quantity": 4}, headers=cust)
    assert res.status_code == 400
    tickets = client.get(f"/api/events/{event_id}/ticket-types").json()
    assert tickets[0]["remaining_quantity"] == 3  # nothing was reserved


# 8
def test_failed_payment_does_not_confirm_booking(client):
    org, cust = _organizer_and_customer(client)
    event_id, ticket_id = published_event_with_tickets(client, org)
    booking = client.post("/api/bookings", data={"event_id": event_id, "ticket_type_id": ticket_id, "quantity": 1}, headers=cust).json()

    res = client.post("/api/payments", data={"booking_id": booking["id"], "outcome": "FAILED"}, headers=cust)
    assert res.status_code == 201
    assert res.json()["status"] == "FAILED"
    assert res.json()["transaction_reference"].startswith("TXN-")

    assert client.get(f"/api/bookings/{booking['id']}", headers=cust).json()["status"] == "PENDING"


# 9
def test_cancel_confirmed_booking_restores_inventory_once(client):
    org, cust = _organizer_and_customer(client)
    event_id, ticket_id = published_event_with_tickets(client, org, regular_qty=5)
    booking = client.post("/api/bookings", data={"event_id": event_id, "ticket_type_id": ticket_id, "quantity": 2}, headers=cust).json()
    client.post("/api/payments", data={"booking_id": booking["id"], "outcome": "SUCCESS"}, headers=cust)
    assert client.get(f"/api/bookings/{booking['id']}", headers=cust).json()["status"] == "CONFIRMED"

    first = client.post(f"/api/bookings/{booking['id']}/cancel", headers=cust)
    assert first.status_code == 200
    assert first.json()["status"] == "CANCELLED"
    assert client.get(f"/api/events/{event_id}/ticket-types").json()[0]["remaining_quantity"] == 5

    second = client.post(f"/api/bookings/{booking['id']}/cancel", headers=cust)
    assert second.status_code == 400
    assert client.get(f"/api/events/{event_id}/ticket-types").json()[0]["remaining_quantity"] == 5  # not restored twice

    payments = client.get(f"/api/payments/booking/{booking['id']}", headers=cust).json()
    assert payments[0]["status"] == "REFUNDED"


# 10
def test_access_another_customers_booking_denied(client):
    org, cust = _organizer_and_customer(client)
    register(client, "other@test.com")
    other = login(client, "other@test.com")
    event_id, ticket_id = published_event_with_tickets(client, org)
    booking = client.post("/api/bookings", data={"event_id": event_id, "ticket_type_id": ticket_id, "quantity": 1}, headers=cust).json()

    res = client.get(f"/api/bookings/{booking['id']}", headers=other)
    assert res.status_code == 403


# 11
def test_customer_cannot_access_admin_reports(client):
    org, cust = _organizer_and_customer(client)
    event_id, _ = published_event_with_tickets(client, org)

    assert client.get("/api/admin/dashboard", headers=cust).status_code == 403
    assert client.get(f"/api/admin/events/{event_id}/sales-report", headers=cust).status_code == 403

    create_admin()
    assert client.get("/api/admin/dashboard", headers=login(client, "admin@test.com")).status_code == 200


# 12
def test_search_events_with_filters(client):
    register(client, "org@test.com", role="ORGANIZER")
    org = login(client, "org@test.com")
    published_event_with_tickets(client, org, title="Python Conference", category="Technology", ticket_price=999.00)
    published_event_with_tickets(client, org, title="Jazz Night", category="Music", ticket_price=299.00)

    res = client.get("/api/events", params={"category": "Technology"})
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Python Conference"

    res = client.get("/api/events", params={"q": "jazz", "max_price": 500})
    assert [e["title"] for e in res.json()["items"]] == ["Jazz Night"]

    res = client.get("/api/events", params={"sort_by": "ticket_price", "order": "desc", "page": 1, "size": 1})
    body = res.json()
    assert body["total"] == 2 and body["pages"] == 2
    assert body["items"][0]["title"] == "Python Conference"

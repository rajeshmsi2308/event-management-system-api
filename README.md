# Event Management System API

A REST API for managing events, ticket types, bookings, simulated payments, cancellations, notifications and admin reports.
Built with **FastAPI**, **MySQL**, **SQLAlchemy ORM**, **Pydantic**, **JWT** and **bcrypt**. Runs on Windows without Docker.

---

## Features

| Module | What it does |
|---|---|
| Authentication | Register, login (JWT), profile view/update, change password, bcrypt password hashing |
| Role-based access | Admin, Organizer, Customer. Admin accounts cannot self-register |
| Events | Create, update, delete (drafts only), status workflow: Draft -> Published -> Cancelled / Completed |
| Ticket types | Regular / VIP etc. with price and inventory; total tickets cannot exceed event capacity |
| Bookings | Unique booking reference, totals calculated by the backend, row locking to prevent overselling |
| Payments | Simulated Success / Failed payments, unique transaction reference, no duplicate processing |
| Cancellation | Customer cancels a booking or organizer cancels an event; seats restored once, paid bookings refunded |
| Search | Keyword, category, venue, date range and price filters, sorting and pagination |
| Notifications | In-app notifications for bookings, payments and cancellations; mark as read |
| Admin | Dashboard (users, events, bookings, revenue, refunds, top events) and event-wise sales report |

---

## Tech Stack

- Python 3.14
- FastAPI + Uvicorn
- MySQL 8.0
- SQLAlchemy 2.0 ORM + PyMySQL
- Pydantic v2 + pydantic-settings
- PyJWT, bcrypt
- pytest + httpx (tests)
- Postman (API collection)

---

## Project Structure

```
event_management_api/
|-- app/
|   |-- main.py              # FastAPI app and routers
|   |-- config.py            # Settings loaded from .env
|   |-- database.py          # Engine, session, Base
|   |-- models/              # 7 SQLAlchemy tables + enums
|   |-- schemas/             # Pydantic request/response models
|   |-- routers/             # auth, users, events, tickets, bookings, payments, notifications, admin
|   |-- services/            # Business logic
|   |-- dependencies/        # JWT auth + role checks
|   |-- utils/               # Password hashing and JWT helpers
|-- tests/                   # pytest tests (12 required scenarios)
|-- postman/                 # Postman collection
|-- init_db.py               # Creates all tables
|-- create_admin.py          # Creates the admin user
|-- .env.example
|-- requirements.txt
|-- README.md
```

### Database tables
`users`, `events`, `ticket_types`, `bookings`, `booking_items`, `payments`, `notifications`
Money is stored as `DECIMAL`, emails and booking references are unique, and all relations use foreign keys.

---

## Setup on Windows

### 1. Prerequisites
- Python 3.12 or newer
- MySQL 8.0 running locally
- Git

### 2. Clone and open the project
```powershell
git clone <your-repo-url>
cd event_management_api
```

### 3. Create and activate a virtual environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies
```powershell
pip install -r requirements.txt
```

### 5. Create the database
In MySQL Workbench or the MySQL command line:
```sql
CREATE DATABASE event_management_db;
```

### 6. Configure environment variables
Copy the example file and fill in your MySQL password and a secret key:
```powershell
copy .env.example .env
```
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/event_management_db
JWT_SECRET_KEY=change-this-to-a-long-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 7. Create the tables and the admin user
```powershell
python init_db.py
python create_admin.py
```
Default admin: `admin@events.com` / `Admin@123` (change it after first login).

### 8. Run the server
```powershell
uvicorn app.main:app --reload
```
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

In Swagger, click **Authorize** and log in with your email as the username.

---

## Running the Tests

```powershell
pytest -v
```
Tests use a separate SQLite file (`test_events.db`), so the MySQL data is never touched.

## Postman

1. Import `postman/Event_Management_API.postman_collection.json`
2. Start the server and make sure the admin exists
3. Run the collection (48 requests, 68 automated checks)

---

## Main Endpoints

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/auth/register` | Public |
| POST | `/api/auth/login` | Public |
| GET / PATCH | `/api/users/me` | Logged in |
| POST | `/api/users/me/change-password` | Logged in |
| GET | `/api/events` (search, filter, sort, paginate) | Public |
| GET | `/api/events/{id}` | Public |
| POST | `/api/events` | Organizer, Admin |
| GET | `/api/events/mine` | Organizer, Admin |
| PATCH | `/api/events/{id}` | Owner, Admin |
| PATCH | `/api/events/{id}/status` | Owner, Admin |
| DELETE | `/api/events/{id}` (drafts only) | Owner, Admin |
| POST / GET | `/api/events/{id}/ticket-types` | Owner, Admin / Public |
| PATCH / DELETE | `/api/ticket-types/{id}` | Owner, Admin |
| POST | `/api/bookings` | Customer |
| GET | `/api/bookings/me` | Logged in |
| GET | `/api/bookings/{id}` | Owner, Admin |
| POST | `/api/bookings/{id}/cancel` | Owner, Admin |
| POST | `/api/payments` | Customer |
| GET | `/api/payments/booking/{booking_id}` | Owner, Admin |
| GET | `/api/notifications/me` | Logged in |
| GET | `/api/notifications/me/unread-count` | Logged in |
| PATCH | `/api/notifications/{id}/read` | Logged in |
| PATCH | `/api/notifications/read-all` | Logged in |
| GET | `/api/admin/dashboard` | Admin |
| GET | `/api/admin/events/{id}/sales-report` | Owner, Admin |
| GET | `/api/admin/users` | Admin |

Search example:
```
GET /api/events?q=python&category=Technology&min_price=100&max_price=1000&sort_by=start_time&order=asc&page=1&size=10
```

---

## Key Business Rules

- **No overselling:** ticket rows are locked (`SELECT ... FOR UPDATE`) during booking, inside one transaction.
- **Backend totals:** prices always come from the database, never from the request.
- **Booking reference:** unique, e.g. `EVT-20261024-A1B2C3`.
- **Payments:** a booking can be paid only once; a failed payment leaves it `PENDING` so the customer can retry.
- **Cancellation:** seats are restored exactly once; a successful payment becomes `REFUNDED`.
- **Event cancellation:** cancels and refunds every active booking for that event and notifies customers.
- **Status workflow:** Draft -> Published or Cancelled; Published -> Cancelled or Completed; Cancelled and Completed are final.
- **Validation:** future event dates, end after start, non-negative prices, positive quantities, ticket totals within capacity.

---

## Test Results

| # | Scenario | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Register with a new email | 201 Created | 201 Created | Pass |
| 2 | Register with an existing email | 409 Conflict | 409 Conflict | Pass |
| 3 | Login with an incorrect password | 401 Unauthorized | 401 Unauthorized | Pass |
| 4 | Create an event without authentication | 401 Unauthorized | 401 Unauthorized | Pass |
| 5 | Customer creates an event | 403 Forbidden | 403 Forbidden | Pass |
| 6 | Book tickets within availability | 201, booking PENDING | 201, booking PENDING | Pass |
| 7 | Book more tickets than available | 400, seats unchanged | 400, seats unchanged | Pass |
| 8 | Simulate a failed payment | Booking not confirmed | Booking stays PENDING | Pass |
| 9 | Cancel a confirmed booking | Seats restored once | Seats restored once, payment REFUNDED | Pass |
| 10 | Access another customer's booking | 403 Forbidden | 403 Forbidden | Pass |
| 11 | Customer accesses admin reports | 403 Forbidden | 403 Forbidden | Pass |
| 12 | Search events using filters | Matching results | Matching results | Pass |

- pytest: **12 passed**
- Postman: **68 / 68 checks passed**

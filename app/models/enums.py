import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ORGANIZER = "ORGANIZER"
    CUSTOMER = "CUSTOMER"


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


# ---- Dropdown choices for Swagger forms ----

class SignupRole(str, enum.Enum):
    """Roles a user can pick when registering (Admin is created by create_admin.py only)."""
    CUSTOMER = "CUSTOMER"
    ORGANIZER = "ORGANIZER"


class EventCategory(str, enum.Enum):
    TECHNOLOGY = "Technology"
    MUSIC = "Music"
    SPORTS = "Sports"
    BUSINESS = "Business"
    EDUCATION = "Education"
    ARTS = "Arts"
    FOOD = "Food"
    COMEDY = "Comedy"
    OTHER = "Other"


class TicketName(str, enum.Enum):
    REGULAR = "Regular"
    STANDARD = "Standard"
    VIP = "VIP"
    PREMIUM = "Premium"
    EARLY_BIRD = "Early Bird"
    STUDENT = "Student"


# Dropdown 1..10 for "how many tickets" (IntEnum so the form value "2" becomes 2)
TicketQuantity = enum.IntEnum("TicketQuantity", {f"QTY_{n}": n for n in range(1, 11)})

from app.database import Base, engine
from app import models  # noqa: F401  (loads all 7 tables)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")
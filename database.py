
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_PASSWORD or not DATABASE_URL:
    raise ValueError(
        "DATABASE_PASSWORD and DATABASE_URL must be set in .env"
    )

# Replace %s in the URL with the encoded database password.
engine = create_engine(
    DATABASE_URL % quote_plus(DATABASE_PASSWORD)
)

# Create a database session factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models.
Base = declarative_base()


# Provide a database session to each request.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

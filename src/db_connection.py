"""Database connection for storing the user requests."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.utils import settings

# Create the SQLAlchemy engine
database_url = settings.DATABASE_URL
engine = create_engine(database_url)

# Create a sessionmaker to manage sessions/connections to the db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI endpoint dependency to get the session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""Database connection for storing the user requests."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"postgresql://admin:password@localhost:5432/bridgeai"


def get_databse_url():
    """Define and return PostgreSQL database URL."""
    """Get the authenticated database url form env vars.

    Example url: "postgresql://admin:password@localhost:5432/databasename"
    """
    # TODO: implemenet the right way to authenticate based on the db setup
    user_name = os.getenv("POSTGRES_USERNAME", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB_NAME", "bridgeai")

    database_url = (
        f"postgresql://{user_name}:{password}@{host}:{port}/{db_name}"
    )

    return database_url


# Create the SQLAlchemy engine
database_url = get_databse_url()
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

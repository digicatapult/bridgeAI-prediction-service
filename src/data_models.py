"""Data models for storing the requests."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Base class for data models to inherit from
Base = declarative_base()


class PredictionLog(Base):
    """Data mapping for database table."""

    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    # Categorical fields
    mainroad = Column(String, nullable=False)
    guestroom = Column(String, nullable=False)
    basement = Column(String, nullable=False)
    hotwaterheating = Column(String, nullable=False)
    airconditioning = Column(String, nullable=False)
    prefarea = Column(String, nullable=False)
    furnishingstatus = Column(String, nullable=False)
    # Numeric fields
    area = Column(Float, nullable=False)
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    stories = Column(Integer, nullable=False)
    parking = Column(Integer, nullable=False)

    prediction_response = Column(Float, nullable=True)  # Prediction result
    timestamp = Column(DateTime, default=datetime.utcnow)  # Log timestamp
    inference_time = Column(Float, nullable=True)  # Inference time

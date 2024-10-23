"""Unit tests for the fastapi app."""

from unittest.mock import patch

import requests
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.data_models import PredictionLog
from src.db_connection import get_db
from src.main import app

# local db setup using docker compose
DB_URL = "postgresql://admin:password@localhost:5432/bridgeai"

# Test payload for model endpoint
PAYLOAD = {
    "mainroad": "yes",
    "guestroom": "no",
    "basement": "yes",
    "hotwaterheating": "no",
    "airconditioning": "yes",
    "prefarea": "no",
    "furnishingstatus": "furnished",
    "area": 1200,
    "bedrooms": 3,
    "bathrooms": 2,
    "stories": 2,
    "parking": 1,
}

engine = create_engine(DB_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    """Override the get_db dependency to use the test session"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Apply the override
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_health_check():
    """Test for health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "message": "success",
        "response": None,
    }


@patch("src.main.requests.post")
def test_get_prediction_service_error(mock_post, monkeypatch):
    """Test when the prediction service is unavailable."""

    def mock_post(*args, **kwargs):
        raise requests.exceptions.RequestException("Service Unavailable")

    monkeypatch.setattr(requests, "post", mock_post)

    response = client.post("/predict", json=PAYLOAD)
    assert response.status_code == 500
    assert (
        "Regression model prediction service error"
        in response.json()["detail"]
    )


@patch("src.main.requests.post")
def test_predict_logs_to_db(mock_post):
    """Integration test for database logging of prediction requests."""
    # Set up the mock response object
    # to mock response from the model prediction endpoint
    mock_post.return_value.status_code = 200
    price = 500000.0
    mock_post.return_value.json.return_value = {
        "model_name": "house_price_prediction_prod",
        "model_version": "4",
        "id": "fa48be92-fa79-4b25-b305-b46c0f877893",
        "parameters": {"content_type": "np"},
        "outputs": [
            {
                "name": "output-1",
                "shape": [1, 1],
                "datatype": "FP32",
                "parameters": {"content_type": "np"},
                "data": [price],
            }
        ],
    }

    response = client.post("/predict", json=PAYLOAD)

    # Check the response status
    assert response.status_code == 200
    assert response.json()["status"] == 200

    # Check if the data is logged in the test database
    db: Session = next(override_get_db())
    log = (
        db.query(PredictionLog)
        .order_by(PredictionLog.timestamp.desc())
        .first()
    )

    assert log is not None
    assert log.mainroad == PAYLOAD["mainroad"]
    assert log.bedrooms == PAYLOAD["bedrooms"]
    assert log.prediction_response == price

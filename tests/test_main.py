"""Unit tests for the fastapi app."""

import requests
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

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


def test_health_check():
    """Test for health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": 200,
        "message": "success",
        "response": None,
    }


def test_get_prediction_service_error(monkeypatch):
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

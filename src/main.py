"""FastAPI prediction service."""

import json
import os
import time
from datetime import datetime, timezone
from typing import Annotated, Literal

import requests
import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from src.data_models import PredictionLog
from src.db_connection import get_db
from src.utils import get_app_version

model_prediction_endpoint = os.getenv(
    "MODEL_PREDICTION_ENDPOINT", "http://localhost:5001/invocations"
)

# custom type
YesNoLiteral = Literal["YES", "yes", "Yes", "NO", "no", "No"]

# Initialise FastAPI app
app = FastAPI(
    title="House price prediction API",
    description="Housing price prediction API "
    "that interacts with MLFlow served model.",
    version=get_app_version(),
    docs_url="/swagger",  # Swagger UI Documentation - default /doc
    redoc_url="/api-docs",  # API documentation - ReDoc - default /redoc
)


class HousingData(BaseModel):
    """House price prediction input data model."""

    # Categorical data
    mainroad: YesNoLiteral
    guestroom: YesNoLiteral
    basement: YesNoLiteral
    hotwaterheating: YesNoLiteral
    airconditioning: YesNoLiteral
    prefarea: YesNoLiteral
    furnishingstatus: Literal["furnished", "unfurnished", "semi-furnished"]
    # Numeric data
    area: int | float
    bedrooms: Annotated[int, Field(lt=10)]
    bathrooms: Annotated[int, Field(lt=10)]
    stories: Annotated[int, Field(lt=5)]
    parking: Annotated[int, Field(lt=10)]

    @field_validator("furnishingstatus", mode="before")
    def normalize_category(cls, v):
        if isinstance(v, str):
            return v.lower()
        raise ValueError("Invalid furnishing status!")


class ResponseModel(BaseModel):
    """General response model."""

    status: int
    message: str
    response: dict


def preprocess_request(data: HousingData):
    """Data transformation for sending the request to the kserve model."""

    # Define datatype mapping for each feature
    datatype_mapping = {
        "mainroad": "BYTES",
        "guestroom": "BYTES",
        "basement": "BYTES",
        "hotwaterheating": "BYTES",
        "airconditioning": "BYTES",
        "prefarea": "BYTES",
        "furnishingstatus": "BYTES",
        "area": "FP32",
        "bedrooms": "INT64",
        "bathrooms": "INT64",
        "stories": "INT64",
        "parking": "INT64",
    }

    # Convert data into dict format
    transformed_data = json.loads(data.model_dump_json())

    # Modify the payload in the required kserve format
    inputs = []
    for key, value in transformed_data.items():
        input_data = {
            "name": key,
            "shape": [1],
            "datatype": datatype_mapping[key],
            "data": [value.upper() if isinstance(value, str) else value],
        }
        inputs.append(input_data)

    payload = {"inputs": inputs}

    # TODO: remove this after testing
    print(payload)

    return payload


@app.post("/predict", response_model=ResponseModel)
def get_prediction(house_data: HousingData, db: Session = Depends(get_db)):
    """Get house price prediction form the model."""
    transformed_payload = preprocess_request(house_data)
    # Log the incoming request to the database
    log_entry = PredictionLog(
        mainroad=house_data.mainroad,
        guestroom=house_data.guestroom,
        basement=house_data.basement,
        hotwaterheating=house_data.hotwaterheating,
        airconditioning=house_data.airconditioning,
        prefarea=house_data.prefarea,
        furnishingstatus=house_data.furnishingstatus,
        area=house_data.area,
        bedrooms=house_data.bedrooms,
        bathrooms=house_data.bathrooms,
        stories=house_data.stories,
        parking=house_data.parking,
    )
    db.add(log_entry)
    db.commit()
    # Refresh the instance to get the ID assigned by the DB
    db.refresh(log_entry)
    log_entry.timestamp = datetime.now(timezone.utc)
    try:
        start_time = time.perf_counter()
        # Get the model prediction

        headers = {"Content-Type": "application/json"}
        response = requests.post(
            model_prediction_endpoint,
            json=transformed_payload,
            headers=headers,
        )

        response.raise_for_status()

        # Extract predicted price from the model endpoint's response
        predicted_price = response.json()["predictions"][0][0]

        # Calculate the inference time in seconds
        end_time = time.perf_counter()
        inference_time = end_time - start_time

        # Log prediction response to the db
        log_entry.prediction_response = predicted_price
        # Log inference time to the db
        log_entry.inference_time = inference_time
        db.commit()

        # Return the response in the expected format
        return {
            "status": 200,
            "message": "House price prediction successful",
            "response": {"prediction": predicted_price, "unit": "GBP(£)"},
        }
    except requests.exceptions.RequestException as e:
        # Log the error and raise an HTTPException
        db.rollback()  # Rollback in case of any exception
        raise HTTPException(
            status_code=500,
            detail=f"Regression model prediction service error: {e}",
        )


@app.get("/health")
def health_check():
    """API health check."""
    # TODO: pass a default valid payload to the
    #  model prediction service and return it in the response
    return {"status": 200, "message": "success", "response": None}


@app.post("/data", response_model=ResponseModel)
def get_data(house_data: HousingData):
    """A test endpoint to see the formatted data passed."""
    # TODO: remove this once the development is completed.
    return {"status": 200, "message": "success", "response": house_data.dict()}


if __name__ == "__main__":
    uvicorn.run(app)

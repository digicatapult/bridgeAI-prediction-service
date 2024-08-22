"""FastAPI prediction service."""

import os
from typing import Annotated, Literal

import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from src.utils import get_app_version

model_prediction_endpoint = os.getenv("MODEL_PREDICTION_ENDPOINT")

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
    """Data transformation sending the request to the model."""
    # include any data transformations needed for the prediction api
    transformed_data = data.model_dump_json()
    return transformed_data


@app.post("/predict", response_model=ResponseModel)
def get_prediction(house_data: HousingData):
    """Get prediction form the model."""
    transformed_payload = preprocess_request(house_data)
    try:
        response = requests.post(
            model_prediction_endpoint, json=transformed_payload
        )
        response.raise_for_status()
        # TODO: format the response to fit the ResponseModel
        return response.json()
    except requests.exceptions.RequestException as e:
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

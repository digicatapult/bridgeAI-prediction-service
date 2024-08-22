# bridgeAI-prediction-service

## How to start the service
1. Install the requirements `poetry install`
2. `cd src`
3. Start the server `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
4. Set up the "MODEL_PREDICTION_ENDPOINT" environment variable to point to the regression model prediction endpoint.
5. Access the swagger ui here - `http://localhost:8000/swagger`
6. The API documentations is available here - `http://localhost:8000/api-docs`

## How to run the test
1. Install the requirements `poetry install`
2. Run the tests `poetry run pytest`

# bridgeAI-prediction-service

## How to start the service
1. Install the requirements `poetry install`
2. Update environment variables needed (see [Environment Variables](#environment-variables))
3. Run `poetry run alembic -c src/alembic.ini upgrade head` for database migration
4. Start the API server `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`
5. Set up the "MODEL_PREDICTION_ENDPOINT" environment variable to point to the regression model prediction endpoint.
6. Access the swagger ui here - `http://localhost:8000/swagger`
7. The API documentations is available here - `http://localhost:8000/api-docs`

### Environment Variables

The following environment variables need to be set:

| Variable                   | Default Value                        | Description                                                  |
|----------------------------|--------------------------------------|--------------------------------------------------------------|
| MODEL_PREDICTION_ENDPOINT  | `http://localhost:5001/invocations`  | The endpoint URL for making model prediction requests.       |
| POSTGRES_HOST              | `localhost`                          | The hostname or IP address of the PostgreSQL server.         |
| POSTGRES_USER              | `admin`                              | The username for authenticating to the PostgreSQL database.  |
| POSTGRES_PASSWORD          | `password`                           | The password for authenticating to the PostgreSQL database.  |
| POSTGRES_DB                | `bridgeai`                           | The name of the PostgreSQL database to connect to.           |
| POSTGRES_PORT              | `5432`                               | The port number on which the PostgreSQL server is listening. |


## How to run the tests
1. Make the database up and running by `docker compose up -d` from terminal
   You can login to the database using `psql -h localhost -p 5432 -U admin -d bridgeai`
1. Install the requirements `poetry install`
2. Run the tests `poetry run pytest`

## Helm installation - local testing
1. To deploy - `helm install prediction-server-release charts/prediction-server-chart`
2. Then port forward - `kubectl port-forward service/prediction-server-release-prediction-server-chart 8000:8000`
3. Check the swagger ui here - `http://localhost:8000/swagger`

Note: To delete the deployment - `helm uninstall prediction-server-release`

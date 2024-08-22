# bridgeAI-prediction-service

## How to start the service
1. Install the requirements `poetry install`
2. `cd src`
3. Start the server `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
4. Access the swagger ui here - `http://localhost:8000/swagger`
5. The API documentations is available here - `http://localhost:8000/api-docs`

## How to run the tests
1. Install the requirements `poetry install`
2. Run the tests `poetry run pytest`

## Helm installation - local testing
1. To deploy - `helm install prediction-server-release charts/prediction-server-chart`
2. Then port forward - `kubectl port-forward service/prediction-server-release-prediction-server-chart 8000:8000`
3. Check the swagger ui here - `http://localhost:8000/swagger`

Note: To delete the deployment - `helm uninstall prediction-server-release`
# AquaMin-AI

AquaMindAI is a lightweight IoT + AI aquaponics monitoring backend.

## Features

- Ingests real-time sensor readings: air temperature, water temperature, humidity, and water level.
- FastAPI endpoints for latest readings, health status, and next-step water temperature prediction.
- Scikit-learn Random Forest model for water temperature trend prediction.
- Dynamic system health score based on safe operating ranges and predicted temperature risk.

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API endpoints

- `POST /api/sensors/readings`
- `GET /api/sensors/latest`
- `GET /api/predictions/water-temperature`
- `GET /api/health`

These endpoints provide the backend data contract needed by a Next.js dashboard for real-time visualization.

## Tests

```bash
python -m pytest -q
```

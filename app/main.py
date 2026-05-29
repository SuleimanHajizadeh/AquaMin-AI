from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor


class SensorReading(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    air_temperature: float = Field(..., ge=-20, le=80)
    water_temperature: float = Field(..., ge=0, le=60)
    humidity: float = Field(..., ge=0, le=100)
    water_level: float = Field(..., ge=0, le=100)


class PredictionResponse(BaseModel):
    predicted_water_temperature: float
    health_score: float
    sample_size: int


app = FastAPI(title="AquaMindAI Monitoring API")
_readings: List[SensorReading] = []


def _range_score(value: float, minimum: float, maximum: float) -> float:
    if minimum <= value <= maximum:
        return 100.0
    distance = minimum - value if value < minimum else value - maximum
    return max(0.0, 100.0 - distance * 10.0)


def compute_health_score(reading: SensorReading, predicted_water_temperature: float | None = None) -> float:
    scores = [
        _range_score(reading.air_temperature, 18, 30),
        _range_score(reading.water_temperature, 20, 28),
        _range_score(reading.humidity, 40, 75),
        _range_score(reading.water_level, 30, 90),
    ]
    if predicted_water_temperature is not None:
        scores.append(_range_score(predicted_water_temperature, 20, 28))
    return round(sum(scores) / len(scores), 2)


def predict_next_water_temperature(readings: List[SensorReading]) -> float:
    if len(readings) < 3:
        return readings[-1].water_temperature

    samples = []
    targets = []
    for idx in range(2, len(readings)):
        samples.append(
            [
                readings[idx - 2].water_temperature,
                readings[idx - 1].water_temperature,
                readings[idx - 1].air_temperature,
                readings[idx - 1].humidity,
                readings[idx - 1].water_level,
            ]
        )
        targets.append(readings[idx].water_temperature)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(samples, targets)

    latest = readings[-1]
    previous = readings[-2]
    prediction = model.predict(
        [[previous.water_temperature, latest.water_temperature, latest.air_temperature, latest.humidity, latest.water_level]]
    )[0]
    return round(float(prediction), 2)


@app.post("/api/sensors/readings", response_model=SensorReading, status_code=201)
def ingest_reading(reading: SensorReading) -> SensorReading:
    _readings.append(reading)
    return reading


@app.get("/api/sensors/latest", response_model=SensorReading)
def get_latest_reading() -> SensorReading:
    if not _readings:
        raise HTTPException(status_code=404, detail="No sensor readings available.")
    return _readings[-1]


@app.get("/api/predictions/water-temperature", response_model=PredictionResponse)
def get_prediction() -> PredictionResponse:
    if not _readings:
        raise HTTPException(status_code=404, detail="No sensor readings available.")
    prediction = predict_next_water_temperature(_readings)
    health = compute_health_score(_readings[-1], predicted_water_temperature=prediction)
    return PredictionResponse(
        predicted_water_temperature=prediction,
        health_score=health,
        sample_size=len(_readings),
    )


@app.get("/api/health")
def get_system_health() -> dict:
    if not _readings:
        return {"status": "waiting_for_data", "health_score": 0.0}
    prediction = predict_next_water_temperature(_readings)
    return {
        "status": "healthy" if compute_health_score(_readings[-1], prediction) >= 70 else "warning",
        "health_score": compute_health_score(_readings[-1], prediction),
        "predicted_water_temperature": prediction,
        "latest_timestamp": _readings[-1].timestamp,
    }

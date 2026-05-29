from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def setup_function() -> None:
    from app.main import _readings

    _readings.clear()


def _sample_payload(water_temperature: float) -> dict:
    return {
        "air_temperature": 25.0,
        "water_temperature": water_temperature,
        "humidity": 60.0,
        "water_level": 70.0,
    }


def test_ingest_and_fetch_latest_reading() -> None:
    response = client.post("/api/sensors/readings", json=_sample_payload(22.5))
    assert response.status_code == 201
    latest = client.get("/api/sensors/latest")
    assert latest.status_code == 200
    assert latest.json()["water_temperature"] == 22.5


def test_prediction_endpoint_uses_random_forest_pipeline() -> None:
    for value in [22.0, 22.3, 22.6, 22.9]:
        assert client.post("/api/sensors/readings", json=_sample_payload(value)).status_code == 201

    prediction = client.get("/api/predictions/water-temperature")
    assert prediction.status_code == 200
    body = prediction.json()
    assert body["sample_size"] == 4
    assert 0 <= body["health_score"] <= 100
    assert isinstance(body["predicted_water_temperature"], float)


def test_health_endpoint_warns_for_bad_conditions() -> None:
    client.post(
        "/api/sensors/readings",
        json={
            "air_temperature": 45.0,
            "water_temperature": 35.0,
            "humidity": 10.0,
            "water_level": 5.0,
        },
    )
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "warning"

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.schemas import SensorReadingCreate, SensorReadingOut
from routers.sensors import create_reading

router = APIRouter()

@router.post("/arduino", response_model=SensorReadingOut)
def arduino_post(data: SensorReadingCreate, db: Session = Depends(get_db)):
    data.source = "arduino"
    return create_reading(data, db)

@router.get("/status")
def hw_status():
    return {
        "arduino": False,
        "sensors": {"DS18B20": False, "HC-SR04": False, "DHT11": False, "Relay": False},
        "message": "Mock data rejimi. Arduino qoşulduqda avtomatik keçəcək."
    }

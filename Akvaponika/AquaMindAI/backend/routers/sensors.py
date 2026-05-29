from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from models.database import get_db, SensorReading
from models.schemas import SensorReadingCreate, SensorReadingOut
from typing import List

router = APIRouter()

@router.get("/latest", response_model=SensorReadingOut)
def get_latest(db: Session = Depends(get_db)):
    r = db.query(SensorReading).order_by(desc(SensorReading.timestamp)).first()
    if not r:
        from services.data_generator import generate_reading
        r = generate_reading(db)
    return r

@router.get("/history", response_model=List[SensorReadingOut])
def get_history(hours: int = Query(24, ge=1, le=168), limit: int = Query(200, ge=10, le=1000), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(hours=hours)
    return db.query(SensorReading).filter(SensorReading.timestamp >= since).order_by(SensorReading.timestamp).limit(limit).all()

@router.post("/reading", response_model=SensorReadingOut)
def create_reading(data: SensorReadingCreate, db: Session = Depends(get_db)):
    from models.ai_engine import AquaMindAI
    r = SensorReading(**data.dict(), timestamp=datetime.utcnow())
    db.add(r); db.commit(); db.refresh(r)
    AquaMindAI().check_alerts(db, r)
    return r

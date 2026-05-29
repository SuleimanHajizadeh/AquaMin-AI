from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db
from models.ai_engine import AquaMindAI

router = APIRouter()
ai = AquaMindAI()

@router.get("/water-temp")
def predict_water_temp(db: Session = Depends(get_db)):
    return ai.predict_water_temp(db)

@router.get("/system-status")
def system_status(db: Session = Depends(get_db)):
    return ai.get_system_status(db)

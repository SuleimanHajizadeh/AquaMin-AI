from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from models.database import get_db, Alert
from models.schemas import AlertOut
from typing import List

router = APIRouter()

@router.get("/active", response_model=List[AlertOut])
def get_active(db: Session = Depends(get_db)):
    return db.query(Alert).filter(Alert.resolved==False).order_by(desc(Alert.timestamp)).limit(10).all()

@router.get("/history", response_model=List[AlertOut])
def get_history(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(desc(Alert.timestamp)).limit(50).all()

@router.post("/{alert_id}/resolve")
def resolve(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(Alert).filter(Alert.id==alert_id).first()
    if a:
        a.resolved = True; a.resolved_at = datetime.utcnow(); db.commit()
        return {"success": True}
    return {"success": False}

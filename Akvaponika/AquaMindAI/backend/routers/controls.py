from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.database import get_db, PumpCommand, SensorReading
from models.schemas import ControlCommand
from sqlalchemy import desc

router = APIRouter()

@router.post("/pump")
def control_pump(cmd: ControlCommand, db: Session = Depends(get_db)):
    # Pump state-i son oxunuşda yenilə
    latest = db.query(SensorReading).order_by(desc(SensorReading.timestamp)).first()
    if latest:
        if cmd.device == "pump":
            latest.pump_status = 1 if cmd.action == "on" else 0
        elif cmd.device == "aerator":
            latest.aerator_status = 1 if cmd.action == "on" else 0
        db.commit()
    # Əmri qeyd et
    command = PumpCommand(pool_id=1, timestamp=datetime.utcnow(),
                          device=cmd.device, action=cmd.action, triggered_by=cmd.triggered_by)
    db.add(command); db.commit()
    return {"success": True, "device": cmd.device, "action": cmd.action}

@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    latest = db.query(SensorReading).order_by(desc(SensorReading.timestamp)).first()
    if not latest:
        return {"pump": False, "aerator": True}
    return {"pump": bool(latest.pump_status), "aerator": bool(latest.aerator_status)}

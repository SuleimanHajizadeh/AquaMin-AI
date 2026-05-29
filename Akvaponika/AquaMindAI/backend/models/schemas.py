from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class SourceEnum(str, Enum):
    mock = "mock"
    arduino = "arduino"
    manual = "manual"

class SensorReadingCreate(BaseModel):
    pool_id: int = 1
    water_temp_c: Optional[float] = None
    water_level_cm: Optional[float] = None
    air_temp_c: Optional[float] = None
    air_humidity_pct: Optional[float] = None
    source: SourceEnum = SourceEnum.mock

class SensorReadingOut(BaseModel):
    id: int
    pool_id: int
    timestamp: datetime
    water_temp_c: Optional[float]
    water_level_cm: Optional[float]
    air_temp_c: Optional[float]
    air_humidity_pct: Optional[float]
    source: str
    class Config:
        from_attributes = True

class AlertOut(BaseModel):
    id: int
    pool_id: int
    timestamp: datetime
    severity: str
    sensor: Optional[str]
    message: Optional[str]
    value: Optional[float]
    threshold_min: Optional[float]
    threshold_max: Optional[float]
    resolved: bool
    class Config:
        from_attributes = True

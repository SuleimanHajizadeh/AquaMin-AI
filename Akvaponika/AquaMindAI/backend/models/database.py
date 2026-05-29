import os
from sqlalchemy import (create_engine, Column, Integer, BigInteger, Float,
                        String, DateTime, Boolean, Enum, Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL","mysql+pymysql://aquamind:AquaMind2024Pass@mysql:3306/aquamind")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    water_temp_c = Column(Float)       # DS18B20
    water_level_cm = Column(Float)     # HC-SR04
    air_temp_c = Column(Float)         # DHT11
    air_humidity_pct = Column(Float)   # DHT11
    source = Column(Enum('mock','arduino','manual'), default='mock')
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.utcnow)
    severity = Column(Enum('critical','warning','info'))
    sensor = Column(String(50))
    message = Column(Text)
    value = Column(Float)
    threshold_min = Column(Float)
    threshold_max = Column(Float)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)

class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pool_id = Column(Integer, default=1)
    predicted_at = Column(DateTime, default=datetime.utcnow)
    target_time = Column(DateTime)
    metric = Column(String(50))
    predicted_value = Column(Float)
    confidence = Column(Float)
    model_used = Column(String(50), default='RandomForest')

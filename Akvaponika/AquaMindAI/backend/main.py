from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.database import engine, Base, SessionLocal
from routers import sensors, predictions, alerts, hardware
from services.scheduler import start_scheduler
from services.data_generator import seed_historical_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_historical_data(db)
    db.close()
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(
    title="AquaMind AI",
    description="Azərbaycan Respublikası — Ağıllı Akvakültur Monitorinq Sistemi",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(sensors.router,     prefix="/api/sensors",     tags=["Sensorlar"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["AI Proqnozlar"])
app.include_router(alerts.router,      prefix="/api/alerts",      tags=["Xəbərdarlıqlar"])
app.include_router(hardware.router,    prefix="/api/hardware",    tags=["Hardware"])

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0", "project": "AquaMind AI", "country": "Azerbaijan"}

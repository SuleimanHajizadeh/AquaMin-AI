from apscheduler.schedulers.background import BackgroundScheduler
from models.database import SessionLocal
from models.ai_engine import AquaMindAI
from services.data_generator import generate_reading

ai = AquaMindAI()

def data_job():
    db = SessionLocal()
    try:
        reading = generate_reading(db)
        ai.check_alerts(db, reading)
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Baku")
    scheduler.add_job(data_job, 'interval', seconds=10, id='sensor_data')
    scheduler.start()
    return scheduler

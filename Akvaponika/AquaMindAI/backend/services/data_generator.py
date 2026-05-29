import random, math
from datetime import datetime
from models.database import SensorReading

def generate_reading(db=None, source="mock"):
    hour = datetime.utcnow().hour

    # DS18B20: Su temperaturu — gündüz artır, gecə azalır
    base_water_temp = 25.5
    daily_cycle = 2.0 * math.sin((hour - 6) * math.pi / 12)
    water_temp = round(base_water_temp + daily_cycle + random.gauss(0, 0.3), 2)

    # HC-SR04: Su səviyyəsi
    water_level = round(95.0 + random.gauss(0, 1.5), 1)
    water_level = max(20.0, min(130.0, water_level))

    # DHT11: Hava temperaturu
    air_temp = round(28.0 + 5.0 * math.sin((hour - 8) * math.pi / 12) + random.gauss(0, 0.5), 1)

    # DHT11: Hava rütubəti
    air_humidity = round(65.0 + 10.0 * math.cos(hour * math.pi / 12) + random.gauss(0, 1.5), 1)
    air_humidity = max(20.0, min(95.0, air_humidity))

    reading = SensorReading(
        pool_id=1,
        timestamp=datetime.utcnow(),
        water_temp_c=water_temp,
        water_level_cm=water_level,
        air_temp_c=air_temp,
        air_humidity_pct=air_humidity,
        source=source
    )
    if db:
        db.add(reading)
        db.commit()
        db.refresh(reading)
    return reading

def seed_historical_data(db):
    from datetime import timedelta
    count = db.query(SensorReading).count()
    if count > 0:
        return
    base_time = datetime.utcnow() - timedelta(hours=48)
    for i in range(288):  # 48 saat, 10 dəqiqəlik intervallarla
        t = base_time + timedelta(minutes=i * 10)
        hour = t.hour
        daily_cycle = 2.0 * math.sin((hour - 6) * math.pi / 12)
        r = SensorReading(
            pool_id=1,
            timestamp=t,
            water_temp_c=round(25.5 + daily_cycle + random.gauss(0, 0.3), 2),
            water_level_cm=round(95.0 + random.gauss(0, 2.0), 1),
            air_temp_c=round(28.0 + 5.0 * math.sin((hour-8)*math.pi/12) + random.gauss(0, 0.5), 1),
            air_humidity_pct=round(max(20, min(95, 65.0 + 10.0*math.cos(hour*math.pi/12) + random.gauss(0, 1.5))), 1),
            source="mock"
        )
        db.add(r)
    db.commit()

"""
AquaMind AI - Sensor Data Generator
Hardware: DS18B20, HC-SR04, DHT11
"""
import pandas as pd
import numpy as np
import math, os, random
from datetime import datetime, timedelta

SENSOR_CONFIG = {
    "su_temp_c": {
        "label": "Su Temperaturu", "hardware": "DS18B20 Waterproof",
        "min": 22.0, "max": 30.0, "critical_low": 15.0, "critical_high": 36.0,
        "unit": "°C", "icon": "🌡️"
    },
    "su_seviyyesi_cm": {
        "label": "Su Səviyyəsi", "hardware": "HC-SR04 Ultrasonik",
        "min": 40.0, "max": 90.0, "critical_low": 20.0, "critical_high": 110.0,
        "unit": "cm", "icon": "💧"
    },
    "hava_temp_c": {
        "label": "Hava Temperaturu", "hardware": "DHT11",
        "min": 15.0, "max": 38.0, "critical_low": 5.0, "critical_high": 45.0,
        "unit": "°C", "icon": "🌤️"
    },
    "hava_rutubet_pct": {
        "label": "Hava Rütubəti", "hardware": "DHT11",
        "min": 40.0, "max": 85.0, "critical_low": 20.0, "critical_high": 95.0,
        "unit": "%", "icon": "💨"
    },
}

def generate_sensor_reading(timestamp, anomaly_prob=0.03):
    hour = timestamp.hour
    su_temp   = round(26.0 + 2.5*math.sin((hour-7)*math.pi/12) + random.gauss(0, 0.15), 2)
    su_sev    = round(max(15.0, min(115.0, 72.0 + random.gauss(0, 1.2))), 1)
    hava_temp = round(27.0 + 6.0*math.sin((hour-8)*math.pi/12) + random.gauss(0, 0.4), 1)
    hava_rut  = round(max(20.0, min(95.0, 65.0 - 8.0*math.sin((hour-8)*math.pi/12) + random.gauss(0, 1.5))), 1)

    reading = {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "su_temp_c": su_temp,
        "su_seviyyesi_cm": su_sev,
        "hava_temp_c": hava_temp,
        "hava_rutubet_pct": hava_rut,
        "manba": "mock"
    }

    if random.random() < anomaly_prob:
        field = random.choice(["su_temp_c", "su_seviyyesi_cm"])
        cfg = SENSOR_CONFIG[field]
        reading[field] = round(cfg["critical_high"] + random.uniform(0.5, 3.0)
                               if random.random() < 0.5 else
                               cfg["critical_low"] - random.uniform(0.5, 2.0), 2)
    return reading

def get_live_reading():
    return generate_sensor_reading(datetime.now(), anomaly_prob=0.05)

def generate_historical_data(hours=48, interval_minutes=5, output_path=None):
    records = []
    now = datetime.now()
    start = now - timedelta(hours=hours)
    current = start
    while current <= now:
        records.append(generate_sensor_reading(current))
        current += timedelta(minutes=interval_minutes)
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
    return df

def classify_status(value, config):
    if value <= config["critical_low"] or value >= config["critical_high"]:
        return "🔴 KRİTİK"
    elif value < config["min"] or value > config["max"]:
        return "🟡 XƏBƏRDARLIQ"
    return "🟢 NORMAL"

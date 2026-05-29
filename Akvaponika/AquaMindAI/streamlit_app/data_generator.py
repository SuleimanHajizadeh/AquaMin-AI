"""
AquaMind AI - Fake Sensor Data Generator
Simulates real-time aquaculture sensor readings without hardware.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import random

# ─── Sensor Normal Ranges ─────────────────────────────────────────────────────
SENSOR_CONFIG = {
    "temperature_c":    {"min": 18.0, "max": 28.0, "critical_low": 15.0, "critical_high": 32.0, "unit": "°C"},
    "water_level_cm":   {"min": 60.0, "max": 90.0, "critical_low": 40.0, "critical_high": 100.0, "unit": "cm"},
    "ph":               {"min": 6.5,  "max": 8.5,  "critical_low": 5.5,  "critical_high": 9.5,  "unit": "pH"},
    "dissolved_oxygen": {"min": 6.0,  "max": 10.0, "critical_low": 4.0,  "critical_high": 12.0, "unit": "mg/L"},
    "turbidity_ntu":    {"min": 0.0,  "max": 30.0, "critical_low": 0.0,  "critical_high": 80.0, "unit": "NTU"},
    "ammonia_ppm":      {"min": 0.0,  "max": 0.5,  "critical_low": 0.0,  "critical_high": 2.0,  "unit": "ppm"},
}

def generate_sensor_reading(timestamp, anomaly_prob=0.05):
    """Generate a single realistic sensor reading with possible anomalies."""
    hour = timestamp.hour
    # Temperature follows daily cycle (warmer afternoon)
    temp_base = 22.0 + 3.0 * np.sin((hour - 6) * np.pi / 12)

    reading = {
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "temperature_c":    round(temp_base + random.gauss(0, 0.5), 2),
        "water_level_cm":   round(random.gauss(75.0, 3.0), 2),
        "ph":               round(random.gauss(7.2, 0.2), 2),
        "dissolved_oxygen": round(random.gauss(8.0, 0.5), 2),
        "turbidity_ntu":    round(abs(random.gauss(10.0, 5.0)), 2),
        "ammonia_ppm":      round(abs(random.gauss(0.1, 0.05)), 3),
    }

    # Inject random anomaly
    if random.random() < anomaly_prob:
        sensor = random.choice(list(SENSOR_CONFIG.keys()))
        config = SENSOR_CONFIG[sensor]
        if random.random() < 0.5:
            reading[sensor] = round(config["critical_low"] - random.uniform(0.5, 2.0), 2)
        else:
            reading[sensor] = round(config["critical_high"] + random.uniform(0.5, 2.0), 2)

    return reading


def generate_historical_data(hours=48, interval_minutes=5, output_path=None):
    """Generate historical sensor data for the past N hours."""
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
        df.to_csv(output_path, index=False)
        print(f"✅ {len(df)} records saved → {output_path}")

    return df


def get_live_reading():
    """Simulate a single live sensor reading (called every refresh)."""
    return generate_sensor_reading(datetime.now(), anomaly_prob=0.08)


def classify_status(value, config):
    """Return status label for a sensor value."""
    if value <= config["critical_low"] or value >= config["critical_high"]:
        return "🔴 KRİTİK"
    elif value < config["min"] or value > config["max"]:
        return "🟡 XƏBƏRDARLIQ"
    else:
        return "🟢 NORMAL"


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    output = os.path.join(data_dir, "sensor_history.csv")
    df = generate_historical_data(hours=48, interval_minutes=5, output_path=output)
    print(df.tail())

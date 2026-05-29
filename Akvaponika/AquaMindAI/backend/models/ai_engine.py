import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy.orm import Session
from models.database import SensorReading, Alert

NORMAL_RANGES = {
    "water_temp_c":    {"min": 22.0, "max": 30.0, "critical_min": 18.0, "critical_max": 35.0,
                        "label": "Su Temperaturu", "unit": "°C"},
    "water_level_cm":  {"min": 40.0, "max": 120.0, "critical_min": 20.0, "critical_max": 130.0,
                        "label": "Su Səviyyəsi", "unit": "cm"},
    "air_temp_c":      {"min": 15.0, "max": 38.0, "critical_min": 5.0, "critical_max": 45.0,
                        "label": "Hava Temperaturu", "unit": "°C"},
    "air_humidity_pct":{"min": 40.0, "max": 85.0, "critical_min": 20.0, "critical_max": 95.0,
                        "label": "Hava Rütubəti", "unit": "%"},
}

class AquaMindAI:
    def _get_recent(self, db: Session, hours: int = 24):
        since = datetime.utcnow() - timedelta(hours=hours)
        return db.query(SensorReading).filter(
            SensorReading.timestamp >= since
        ).order_by(SensorReading.timestamp).all()

    def predict_water_temp(self, db: Session) -> dict:
        readings = self._get_recent(db, 48)
        latest = db.query(SensorReading).order_by(
            SensorReading.timestamp.desc()).first()
        base = latest.water_temp_c if latest and latest.water_temp_c else 25.0
        if len(readings) < 12:
            variation = np.random.uniform(-0.3, 0.3)
            return {
                "metric": "water_temp_c",
                "label": "Su Temperaturu",
                "current": round(base, 2),
                "predicted_1h": round(base + variation, 2),
                "predicted_3h": round(base + variation * 2, 2),
                "predicted_6h": round(base + variation * 2.5, 2),
                "confidence": 0.68,
                "trend": "stable",
                "unit": "°C"
            }
        temps = [r.water_temp_c for r in readings if r.water_temp_c]
        X = np.array(range(len(temps))).reshape(-1, 1)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, np.array(temps))
        n = len(temps)
        p1 = float(model.predict([[n]])[0])
        p3 = float(model.predict([[n+2]])[0])
        p6 = float(model.predict([[n+5]])[0])
        trend = "rising" if p6 > base + 0.5 else "falling" if p6 < base - 0.5 else "stable"
        return {
            "metric": "water_temp_c",
            "label": "Su Temperaturu",
            "current": round(base, 2),
            "predicted_1h": round(p1, 2),
            "predicted_3h": round(p3, 2),
            "predicted_6h": round(p6, 2),
            "confidence": 0.85,
            "trend": trend,
            "unit": "°C"
        }

    def check_alerts(self, db: Session, reading: SensorReading):
        for field, ranges in NORMAL_RANGES.items():
            val = getattr(reading, field, None)
            if val is None:
                continue
            severity = None
            if val < ranges["critical_min"] or val > ranges["critical_max"]:
                severity = "critical"
            elif val < ranges["min"] or val > ranges["max"]:
                severity = "warning"
            if severity:
                alert = Alert(
                    pool_id=1,
                    timestamp=datetime.utcnow(),
                    severity=severity,
                    sensor=field,
                    message=f"{ranges['label']}: {val}{ranges['unit']} — normal aralıq [{ranges['min']}–{ranges['max']}]",
                    value=val,
                    threshold_min=ranges["min"],
                    threshold_max=ranges["max"]
                )
                db.add(alert)
        db.commit()

    def get_system_status(self, db: Session) -> dict:
        latest = db.query(SensorReading).order_by(
            SensorReading.timestamp.desc()).first()
        if not latest:
            return {"status": "no_data", "score": 0, "summary": "Məlumat yoxdur"}
        score = 100
        issues = []
        r = NORMAL_RANGES
        if latest.water_temp_c:
            if not (r["water_temp_c"]["min"] <= latest.water_temp_c <= r["water_temp_c"]["max"]):
                score -= 25
                issues.append("Su temperaturu normadan kənardadır")
        if latest.water_level_cm:
            if not (r["water_level_cm"]["min"] <= latest.water_level_cm <= r["water_level_cm"]["max"]):
                score -= 25
                issues.append("Su səviyyəsi normadan kənardadır")
        if latest.air_humidity_pct:
            if not (r["air_humidity_pct"]["min"] <= latest.air_humidity_pct <= r["air_humidity_pct"]["max"]):
                score -= 10
                issues.append("Hava rütubəti normadan kənardadır")
        score = max(score, 0)
        if score >= 90:
            status = "excellent"
            summary = "Sistem mükəmməl işləyir"
        elif score >= 70:
            status = "good"
            summary = "Sistem yaxşı vəziyyətdədir"
        elif score >= 50:
            status = "warning"
            summary = "Diqqət tələb edir"
        else:
            status = "critical"
            summary = "Kritik vəziyyət"
        return {"status": status, "score": score, "summary": summary, "issues": issues}

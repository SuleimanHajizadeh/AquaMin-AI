"""
AquaMind AI - Machine Learning Engine
Real hardware sensorlarına uyğun: DS18B20, HC-SR04, DHT11
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os

MODEL_DIR = os.path.join(os.path.dirname(__file__))
os.makedirs(MODEL_DIR, exist_ok=True)

# Yalnız mövcud hardware sensorları üçün hədd dəyərləri
THRESHOLDS = {
    "su_temp_c":       (15.0, 36.0),   # DS18B20
    "su_seviyyesi_cm": (20.0, 110.0),  # HC-SR04
    "hava_temp_c":     (5.0,  45.0),   # DHT11
    "hava_rutubet_pct": (20.0, 95.0),  # DHT11
}

SENSOR_FEATURES = ["su_temp_c", "su_seviyyesi_cm", "hava_temp_c", "hava_rutubet_pct"]


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["hour"] = df["timestamp"].dt.hour
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24)
    for col in SENSOR_FEATURES:
        if col in df.columns:
            df[f"{col}_lag1"] = df[col].shift(1)
            df[f"{col}_roll3"] = df[col].rolling(3).mean()
    df.dropna(inplace=True)
    return df


class TemperaturePredictor:
    """DS18B20 su temperaturu üçün RandomForest proqnozu."""
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False
        self.features = [
            "sin_hour", "cos_hour",
            "su_temp_c_lag1", "su_temp_c_roll3",
            "hava_temp_c_lag1"
        ]

    def train(self, df: pd.DataFrame):
        df_feat = _engineer_features(df)
        # Yalnız mövcud feature-ləri istifadə et
        available = [f for f in self.features if f in df_feat.columns]
        if not available:
            return 0
        X = df_feat[available]
        y = df_feat["su_temp_c"]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
        self.scaler.fit(X_tr)
        self.model.fit(self.scaler.transform(X_tr), y_tr)
        score = self.model.score(self.scaler.transform(X_te), y_te)
        self.trained = True
        self.features = available
        self._save()
        return score

    def predict_next_hours(self, df: pd.DataFrame, hours=6) -> list:
        if not self.trained:
            return []
        df_feat = _engineer_features(df)
        last = df_feat.iloc[-1].copy()
        preds = []
        future = pd.to_datetime(last["timestamp"])
        for i in range(1, hours + 1):
            future += pd.Timedelta(hours=1)
            last["sin_hour"] = np.sin(2 * np.pi * future.hour / 24)
            last["cos_hour"] = np.cos(2 * np.pi * future.hour / 24)
            X = pd.DataFrame([last[self.features]])
            pred = float(self.model.predict(self.scaler.transform(X))[0])
            preds.append({
                "saat": future.strftime("%H:%M"),
                "proqnoz_su_temp": round(pred, 2)
            })
            if "su_temp_c_lag1" in self.features:
                last["su_temp_c_lag1"] = pred
            if "su_temp_c_roll3" in self.features:
                last["su_temp_c_roll3"] = pred
        return preds

    def _save(self):
        with open(os.path.join(MODEL_DIR, "temp_predictor.pkl"), "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler,
                         "features": self.features, "trained": self.trained}, f)

    def load(self):
        path = os.path.join(MODEL_DIR, "temp_predictor.pkl")
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    d = pickle.load(f)
                self.model = d["model"]
                self.scaler = d["scaler"]
                self.features = d.get("features", self.features)
                self.trained = d.get("trained", True)
                return True
            except Exception:
                pass
        return False


class AnomalyDetector:
    """Isolation Forest ilə real sensor anomaliyası."""
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False
        self.features = SENSOR_FEATURES

    def train(self, df: pd.DataFrame):
        available = [f for f in self.features if f in df.columns]
        if not available:
            return
        X = df[available].dropna()
        self.scaler.fit(X)
        self.model.fit(self.scaler.transform(X))
        self.trained = True
        self.features = available
        self._save()

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        available = [f for f in self.features if f in df.columns]
        if not available or not self.trained:
            df["is_anomaly"] = False
            df["anomaly_score"] = 0.0
            return df
        X = df[available].fillna(df[available].mean())
        X_sc = self.scaler.transform(X)
        df["is_anomaly"] = self.model.predict(X_sc) == -1
        df["anomaly_score"] = self.model.score_samples(X_sc)
        return df

    def detect_single(self, reading: dict) -> dict:
        if not self.trained:
            return {"is_anomaly": False, "anomaly_score": 0.0}
        row = {k: reading.get(k, 0) for k in self.features}
        X = pd.DataFrame([row])
        X_sc = self.scaler.transform(X)
        pred = self.model.predict(X_sc)[0]
        score = self.model.score_samples(X_sc)[0]
        return {"is_anomaly": pred == -1, "anomaly_score": round(score, 4)}

    def _save(self):
        with open(os.path.join(MODEL_DIR, "anomaly_detector.pkl"), "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler,
                         "features": self.features, "trained": self.trained}, f)

    def load(self):
        path = os.path.join(MODEL_DIR, "anomaly_detector.pkl")
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    d = pickle.load(f)
                self.model = d["model"]
                self.scaler = d["scaler"]
                self.features = d.get("features", self.features)
                self.trained = d.get("trained", True)
                return True
            except Exception:
                pass
        return False


def calculate_risk_score(reading: dict) -> dict:
    """Yalnız mövcud sensorlara əsasən risk hesabla."""
    violations = []
    for sensor, (low, high) in THRESHOLDS.items():
        val = reading.get(sensor)
        if val is None:
            continue
        if val < low or val > high:
            severity = abs(val - (low if val < low else high))
            violations.append({
                "sensor": sensor,
                "value": val,
                "severity": round(severity, 2)
            })
    risk = min(100, len(violations) * 30 + sum(v["severity"] * 4 for v in violations))
    level = "🔴 KRİTİK" if risk >= 70 else "🟡 ORTA" if risk >= 30 else "🟢 AŞAĞI"
    return {"score": round(risk, 1), "level": level, "violations": violations}

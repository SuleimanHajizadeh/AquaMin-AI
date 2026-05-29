# 🌊 AquaMindAI

<img width="498" height="498" alt="image" src="https://github.com/user-attachments/assets/c5c532aa-c2c3-4f9d-a291-4638f9b38826" />


AquaMindAI is an enterprise-grade IoT and AI-driven monitoring system designed to manage and optimize aquaponics ecosystems. By connecting physical sensors to a cloud database, AquaMindAI provides real-time data visualization, automated anomaly detection, and machine-learning-based forecasting to ensure optimal conditions for both fish and plants.

## 🛠️ Tech Stack & Architecture

- **Hardware & IoT:** Arduino Uno (ATmega328P), DHT11 (Air Temp & Humidity), HC-SR04 (Water Level), DS18B20 (Water Temperature).
- **Backend API:** FastAPI (Python), SQLAlchemy, PyMySQL, Uvicorn, APScheduler.
- **Database:** MySQL 8.0 (Dockerized).
- **Machine Learning Engine:** Scikit-Learn (Random Forest Regressor for temperature forecasting), NumPy, Pandas.
- **Frontend App:** Next.js (TypeScript, Tailwind CSS) for the main operator dashboard & Streamlit for developer simulation and metrics.
- **DevOps:** Docker, Docker Compose for seamless cross-platform orchestration.

## ✨ Key Features

- **Real-time Synchronization:** Sub-second sensor updates routed from hardware endpoints directly to the database and frontend.
- **AI-Powered Predictions:** Dynamic temperature forecasting for 1h, 3h, and 6h windows using machine learning models to prevent critical overheating or freezing.
- **Smart Alerting:** Automatic categorization of warnings (Warning/Critical) if sensor values deviate from agronomic safety thresholds.
- **System Health Scoring:** A calculated metric from 0-100 indicating the current physiological stability of the aquaponics ecosystem.

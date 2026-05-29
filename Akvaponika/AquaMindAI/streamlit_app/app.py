"""
AquaMind AI - Streamlit Dashboard
Mövcud hardware: HC-SR04, DHT11, DS18B20
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time, math, random

from scripts.data_generator import (
    generate_historical_data, get_live_reading,
    classify_status, SENSOR_CONFIG
)
from models.ai_engine import (
    TemperaturePredictor, AnomalyDetector, calculate_risk_score
)

THRESHOLDS = {
    "su_temp_c":        (15.0, 36.0),
    "su_seviyyesi_cm":  (20.0, 110.0),
    "hava_temp_c":      (5.0,  45.0),
    "hava_rutubet_pct": (20.0, 95.0),
}

# ─── Model yüklə / öyrət ──────────────────────────────────────────────────────
@st.cache_resource
def load_models(df):
    temp_model    = TemperaturePredictor()
    anomaly_model = AnomalyDetector()
    try:
        if not temp_model.load():
            temp_model.train(df)
        if not anomaly_model.load():
            anomaly_model.train(df)
    except Exception:
        temp_model.train(df)
        anomaly_model.train(df)
    return temp_model, anomaly_model

@st.cache_data(ttl=300)
def get_history(hours):
    data_path = os.path.join(os.path.dirname(__file__), "data", "sensor_history.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path, parse_dates=["timestamp"])
        required = ["su_temp_c", "su_seviyyesi_cm", "hava_temp_c", "hava_rutubet_pct"]
        if not all(c in df.columns for c in required):
            df = generate_historical_data(hours=hours, interval_minutes=5, output_path=data_path)
    else:
        df = generate_historical_data(hours=hours, interval_minutes=5, output_path=data_path)
    return df

# ─── Səhifə konfiqurasiyası ──────────────────────────────────────────────────
st.set_page_config(
    page_title="AquaMind AI — Akvakültur Monitorinqi",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; background-color:#050d1a; color:#e0f2fe; }
.stApp { background: linear-gradient(135deg,#050d1a 0%,#071a2e 50%,#050d1a 100%); }
.alert-critical { background:linear-gradient(90deg,rgba(239,68,68,0.2),rgba(239,68,68,0.05)); border-left:4px solid #ef4444; border-radius:8px; padding:12px 16px; margin:4px 0; }
.alert-warning  { background:linear-gradient(90deg,rgba(245,158,11,0.2),rgba(245,158,11,0.05)); border-left:4px solid #f59e0b; border-radius:8px; padding:12px 16px; margin:4px 0; }
.alert-ok       { background:linear-gradient(90deg,rgba(16,185,129,0.2),rgba(16,185,129,0.05)); border-left:4px solid #10b981; border-radius:8px; padding:12px 16px; margin:4px 0; }
.hw-badge { display:inline-block; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); border-radius:6px; padding:2px 10px; font-size:0.72rem; color:#7dd3fc; margin-top:4px; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#071a2e,#050d1a); border-right:1px solid rgba(0,149,255,0.15); }
[data-testid="stMetricValue"] { font-size:2.1rem !important; font-weight:700 !important; }
[data-testid="stMetricLabel"] { font-size:0.82rem !important; color:#7dd3fc !important; }
h1,h2,h3 { color:#7dd3fc !important; }
h1 { font-weight:800 !important; }
</style>
""", unsafe_allow_html=True)

if "live_readings" not in st.session_state:
    st.session_state.live_readings = []

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌊 AquaMind AI")
    st.markdown("**v2.0** · Akvakültur Monitorinq Sistemi")
    st.divider()
    auto_refresh = st.toggle("🔄 Avtomatik yeniləmə", value=True)
    refresh_interval = st.select_slider(
        "Yeniləmə intervalı",
        options=[5, 10, 15, 30, 60], value=10,
        format_func=lambda x: f"{x} saniyə"
    )
    st.divider()
    hours_to_show = st.selectbox(
        "📊 Tarix aralığı", [6, 12, 24, 48], index=1,
        format_func=lambda x: f"Son {x} saat"
    )
    st.divider()
    st.markdown("**🔩 Qoşulmuş Hardware**")
    for hw, func in [("DS18B20","Su Temperaturu"), ("HC-SR04","Su Səviyyəsi"), ("DHT11","Hava Temp + Rütubət"), ("Arduino Uno","Mərkəzi İdarəetmə")]:
        st.caption(f"🔌 **{hw}** — {func}")
    st.divider()
    st.markdown("<small>🟡 Mock rejim — Arduino qoşulanda real data keçər</small>", unsafe_allow_html=True)

# ─── Başlıq ──────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([3, 1.5, 1])
with c1:
    st.markdown("# 🌊 AquaMind AI Dashboard")
    st.caption("Azərbaycan Respublikası — Ağıllı Akvakültur Monitorinq Sistemi · v2.0")
with c2:
    st.metric("🕐 Bakı Vaxtı", datetime.now().strftime("%H:%M:%S"))
with c3:
    st.metric("📡 Status", "🟡 Mock")

st.divider()

# ─── Data yüklə ───────────────────────────────────────────────────────────────
hist_df = get_history(hours_to_show)
temp_model, anomaly_model = load_models(hist_df)

live = get_live_reading()
st.session_state.live_readings.append(live)
if len(st.session_state.live_readings) > 200:
    st.session_state.live_readings = st.session_state.live_readings[-200:]

live_df = pd.DataFrame(st.session_state.live_readings)
live_df["timestamp"] = pd.to_datetime(live_df["timestamp"])

risk = calculate_risk_score(live)
anomaly_result = anomaly_model.detect_single(live)

# ─── Risk banneri ────────────────────────────────────────────────────────────
if risk["score"] >= 70:
    st.markdown(f'<div class="alert-critical">⚠️ <strong>KRİTİK RİSK [{risk["score"]}/100]</strong> — {", ".join(v["sensor"] for v in risk["violations"])} dəyərləri normadan çıxıb!</div>', unsafe_allow_html=True)
elif risk["score"] >= 30:
    st.markdown(f'<div class="alert-warning">⚡ <strong>XƏBƏRDARLIQ [{risk["score"]}/100]</strong> — {", ".join(v["sensor"] for v in risk["violations"])} yoxlanılsın.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="alert-ok">✅ <strong>Sistem Normal [{risk["score"]}/100]</strong> — Bütün parametrlər normadadır.</div>', unsafe_allow_html=True)

if anomaly_result["is_anomaly"]:
    st.warning(f"🔍 AI Anomaliya aşkarladı! Skor: {anomaly_result['anomaly_score']:.4f}")

st.markdown("<br>", unsafe_allow_html=True)

# ─── 4 Sensor kartı ──────────────────────────────────────────────────────────
st.subheader("📊 Canlı Sensor Oxunuşları")
col1, col2, col3, col4 = st.columns(4)

for col, key in zip([col1, col2, col3, col4], SENSOR_CONFIG.keys()):
    cfg = SENSOR_CONFIG[key]
    val = live.get(key, 0)
    status = classify_status(val, cfg)
    with col:
        st.metric(f"{cfg['icon']} {cfg['label']}", f"{val} {cfg['unit']}", delta=status)
        st.markdown(f'<span class="hw-badge">{cfg["hardware"]}</span>', unsafe_allow_html=True)
        if key == "su_seviyyesi_cm":
            pct = int(min(100, max(0, (val / 110) * 100)))
            st.progress(pct)

# ─── Qrafiklər ───────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📈 Sensor Qrafikləri")

cutoff = datetime.now() - timedelta(hours=hours_to_show)
hist_slice = hist_df[hist_df["timestamp"] >= cutoff].copy()
if not live_df.empty:
    combined = pd.concat([hist_slice, live_df], ignore_index=True)
    combined = combined.drop_duplicates(subset="timestamp").sort_values("timestamp")
else:
    combined = hist_slice

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e0f2fe"), height=330,
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    legend=dict(bgcolor="rgba(0,0,0,0.3)")
)

tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Su Temperaturu", "💧 Su Səviyyəsi", "🌤️ Hava", "🤖 AI Proqnoz"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=combined["timestamp"], y=combined["su_temp_c"], mode="lines", name="DS18B20", line=dict(color="#38bdf8", width=2.5), fill="tozeroy", fillcolor="rgba(56,189,248,0.07)"))
    cfg = SENSOR_CONFIG["su_temp_c"]
    fig.add_hline(y=cfg["min"], line_dash="dash", line_color="#f59e0b", annotation_text=f"Min ({cfg['min']}°C)")
    fig.add_hline(y=cfg["max"], line_dash="dash", line_color="#f59e0b", annotation_text=f"Max ({cfg['max']}°C)")
    fig.add_hline(y=cfg["critical_high"], line_dash="dot", line_color="#ef4444", annotation_text="Kritik")
    fig.update_layout(**LAYOUT, yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="°C"))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=combined["timestamp"], y=combined["su_seviyyesi_cm"], mode="lines", name="HC-SR04", line=dict(color="#34d399", width=2.5), fill="tozeroy", fillcolor="rgba(52,211,153,0.07)"))
    cfg = SENSOR_CONFIG["su_seviyyesi_cm"]
    fig.add_hrect(y0=cfg["min"], y1=cfg["max"], fillcolor="rgba(52,211,153,0.06)", line_width=0, annotation_text="Normal Zona")
    fig.add_hline(y=cfg["critical_low"], line_dash="dot", line_color="#ef4444", annotation_text="Kritik aşağı")
    fig.update_layout(**LAYOUT, yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="cm"))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=combined["timestamp"], y=combined["hava_temp_c"], mode="lines", name="DHT11 — Hava Temp", line=dict(color="#fb923c", width=2)))
    fig.add_trace(go.Scatter(x=combined["timestamp"], y=combined["hava_rutubet_pct"], mode="lines", name="DHT11 — Rütubət (%)", line=dict(color="#a78bfa", width=2), yaxis="y2"))
    fig.update_layout(**LAYOUT, yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Temp (°C)"), yaxis2=dict(overlaying="y", side="right", title="Rütubət (%)"))
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### 🤖 Su Temperaturu Proqnozu — DS18B20 (növbəti 6 saat)")
    with st.spinner("RandomForest hesablayır..."):
        try:
            preds = temp_model.predict_next_hours(hist_df, hours=6)
            if preds:
                pred_df = pd.DataFrame(preds)
                last_48 = combined.tail(50)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=last_48["timestamp"], y=last_48["su_temp_c"], mode="lines", name="Faktiki (DS18B20)", line=dict(color="#38bdf8", width=2)))
                now = datetime.now()
                future_ts = [now + timedelta(hours=i+1) for i in range(6)]
                fig.add_trace(go.Scatter(x=future_ts, y=pred_df["proqnoz_su_temp"], mode="lines+markers", name="AI Proqnoz", line=dict(color="#f472b6", width=2, dash="dash"), marker=dict(size=8, color="#f472b6")))
                fig.update_layout(**LAYOUT, yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="°C"))
                st.plotly_chart(fig, use_container_width=True)
                pred_df.columns = ["Saat", "Proqnoz Su Temp (°C)"]
                st.dataframe(pred_df, use_container_width=True, hide_index=True)
            else:
                st.info("Model öyrənilir, bir az data lazımdır...")
        except Exception as e:
            st.error(f"Proqnoz xətası: {e}")

# ─── Anomaliya + Statistika ───────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_anom, col_stats = st.columns([1.5, 1])

with col_anom:
    st.subheader("🔍 Anomaliya Analizi")
    try:
        anom_df = anomaly_model.detect(hist_df.tail(200))
        anomalies = anom_df[anom_df["is_anomaly"] == True][["timestamp", "su_temp_c", "su_seviyyesi_cm", "hava_temp_c", "anomaly_score"]].tail(10)
        if len(anomalies) > 0:
            anomalies.columns = ["Vaxt", "Su Temp °C", "Su Səv cm", "Hava Temp °C", "Anomaliya Skoru"]
            st.dataframe(anomalies, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Son 200 oxunuşda anomaliya tapılmadı.")
    except Exception as e:
        st.warning(f"Anomaliya analizi: {e}")

with col_stats:
    st.subheader("📈 Statistika")
    recent = combined.tail(50)
    stats_data = {
        "Parametr": ["Min Su Temp", "Max Su Temp", "Ort Su Temp", "Min Səviyyə", "Max Səviyyə", "Ort Hava Temp", "Ort Rütubət"],
        "Dəyər": [f"{recent['su_temp_c'].min():.1f}°C", f"{recent['su_temp_c'].max():.1f}°C", f"{recent['su_temp_c'].mean():.1f}°C", f"{recent['su_seviyyesi_cm'].min():.1f}cm", f"{recent['su_seviyyesi_cm'].max():.1f}cm", f"{recent['hava_temp_c'].mean():.1f}°C", f"{recent['hava_rutubet_pct'].mean():.1f}%"]
    }
    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("<center><small>AquaMind AI v2.0 · Azərbaycan Respublikası, Bakı 2025<br>FastAPI · MySQL · Next.js · Streamlit · Scikit-learn · Arduino</small></center>", unsafe_allow_html=True)

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

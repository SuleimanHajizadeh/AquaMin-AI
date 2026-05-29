"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [latest, setLatest] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [waterForecast, setWaterForecast] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("water_temp");

  const fetchAll = useCallback(async () => {
    try {
      const [resLatest, resHist, resAlerts, resStatus, resForecast] = await Promise.all([
        fetch(`${API_URL}/api/sensors/latest`).then(res => res.json()),
        fetch(`${API_URL}/api/sensors/history?hours=24`).then(res => res.json()),
        fetch(`${API_URL}/api/alerts/active`).then(res => res.json()),
        fetch(`${API_URL}/api/predictions/system-status`).then(res => res.json()),
        fetch(`${API_URL}/api/predictions/water-temp`).then(res => res.json())
      ]);
      setLatest(resLatest);
      setHistory(resHist);
      setAlerts(resAlerts);
      setSystemStatus(resStatus);
      setWaterForecast(resForecast);
    } catch (err) {
      console.error("API Fetch Error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 10000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const handleResolveAlert = async (id: number) => {
    try {
      await fetch(`${API_URL}/api/alerts/${id}/resolve`, { method: "POST" });
      fetchAll();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-[#38bdf8] text-xl font-medium">Sistem Yüklənir...</div>;
  }

  const chartData = history.map((item: any) => ({
    time: new Date(item.timestamp).toLocaleTimeString('az-AZ', { hour: '2-digit', minute: '2-digit' }),
    water_temp: item.water_temp_c,
    water_level: item.water_level_cm,
    air_temp: item.air_temp_c,
    humidity: item.air_humidity_pct
  }));

  const getTempColor = (t: number) => t > 35 ? '#ef4444' : t > 30 ? '#f59e0b' : '#22c55e';
  const getLevelColor = (l: number) => l < 40 ? '#ef4444' : l > 120 ? '#ef4444' : l < 60 ? '#f59e0b' : '#22c55e';

  return (
    <div className="min-h-screen bg-[#030f1a] text-[#e2e8f0] p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* HEADER */}
        <header className="glass p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-4xl font-bold gradient-text flex items-center gap-2">🌊 AquaMind AI</h1>
            <p className="text-[#94a3b8] mt-2">Azərbaycan Respublikası — Akvakültur İntelligent Monitorinq Sistemi</p>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="live-dot w-3 h-3 bg-[#22c55e] rounded-full glow-green"></span>
              <span className="text-[#22c55e] font-semibold tracking-widest">CANLI</span>
            </div>
            <div className="text-[#38bdf8] bg-[#38bdf8]/10 px-3 py-1 rounded border border-[#38bdf8]/20">
              {new Date().toLocaleTimeString('az-AZ')}
            </div>
          </div>
        </header>

        {/* SENSOR KARTLARI */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* DS18B20 */}
          <div className="glass p-6 rounded-2xl card-hover relative overflow-hidden group">
            <p className="text-[#94a3b8] text-sm font-medium mb-1 uppercase tracking-wider">Su Temperaturu</p>
            <div className="flex items-end gap-2">
              <h2 className="text-4xl font-bold" style={{color: latest ? getTempColor(latest.water_temp_c) : '#fff'}}>
                {latest?.water_temp_c?.toFixed(1) || '--'}°C
              </h2>
              {waterForecast && (
                <span className={`text-lg mb-1 ${waterForecast.trend === 'rising' ? 'text-[#ef4444]' : waterForecast.trend === 'falling' ? 'text-[#38bdf8]' : 'text-[#94a3b8]'}`}>
                  {waterForecast.trend === 'rising' ? '↑' : waterForecast.trend === 'falling' ? '↓' : '→'}
                </span>
              )}
            </div>
            <p className="text-xs text-[#94a3b8] mt-3">DS18B20 Sensoru</p>
            <p className="text-xs text-[#22c55e] mt-1">Normal aralıq: 22°C – 30°C</p>
          </div>

          {/* HC-SR04 */}
          <div className="glass p-6 rounded-2xl card-hover">
            <p className="text-[#94a3b8] text-sm font-medium mb-1 uppercase tracking-wider">Su Səviyyəsi</p>
            <h2 className="text-4xl font-bold" style={{color: latest ? getLevelColor(latest.water_level_cm) : '#fff'}}>
              {latest?.water_level_cm?.toFixed(1) || '--'} cm
            </h2>
            <div className="w-full bg-[#0a1628] h-2 mt-4 rounded-full overflow-hidden">
              <div className="h-full bg-[#38bdf8] transition-all duration-1000" style={{ width: `${Math.min(100, Math.max(0, ((latest?.water_level_cm || 0) / 120) * 100))}%` }}></div>
            </div>
            <p className="text-xs text-[#94a3b8] mt-3">HC-SR04 Ultrasəs</p>
          </div>

          {/* DHT11 Temp */}
          <div className="glass p-6 rounded-2xl card-hover flex flex-col justify-between">
            <div>
              <p className="text-[#94a3b8] text-sm font-medium mb-1 uppercase tracking-wider flex justify-between">Hava Temp <span>🌡</span></p>
              <h2 className="text-4xl font-bold text-white">{latest?.air_temp_c?.toFixed(1) || '--'}°C</h2>
            </div>
            <p className="text-xs text-[#94a3b8] mt-3">DHT11 Sensoru</p>
          </div>

          {/* DHT11 Hum */}
          <div className="glass p-6 rounded-2xl card-hover flex flex-col justify-between">
            <div>
              <p className="text-[#94a3b8] text-sm font-medium mb-1 uppercase tracking-wider flex justify-between">Hava Rütubəti <span>💧</span></p>
              <h2 className="text-4xl font-bold text-[#38bdf8]">{latest?.air_humidity_pct?.toFixed(1) || '--'}%</h2>
            </div>
            <p className="text-xs text-[#94a3b8] mt-3">DHT11 Sensoru</p>
          </div>
        </div>

        {/* AI PROQNOZ */}
        <div className="grid grid-cols-1 gap-6">
          {/* AI Forecast */}
          <div className="glass p-6 rounded-2xl w-full">
            <h3 className="text-lg font-bold text-[#38bdf8] mb-4">🤖 Süni İntellekt Proqnozu (Su Temp)</h3>
            {waterForecast ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-[#0a1628] rounded-xl border border-[#38bdf8]/20">
                  <p className="text-[#94a3b8] text-xs mb-1">Cari</p>
                  <p className="text-2xl font-bold">{waterForecast.current}°C</p>
                </div>
                <div className="p-4 bg-[#0a1628] rounded-xl border border-[#38bdf8]/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent to-[#38bdf8]"></div>
                  <p className="text-[#94a3b8] text-xs mb-1">1 Saat Sonra</p>
                  <p className="text-2xl font-bold">{waterForecast.predicted_1h}°C</p>
                </div>
                <div className="p-4 bg-[#0a1628] rounded-xl border border-[#38bdf8]/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent to-[#38bdf8] opacity-70"></div>
                  <p className="text-[#94a3b8] text-xs mb-1">3 Saat Sonra</p>
                  <p className="text-2xl font-bold">{waterForecast.predicted_3h}°C</p>
                </div>
                <div className="p-4 bg-[#0a1628] rounded-xl border border-[#38bdf8]/20 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent to-[#38bdf8] opacity-40"></div>
                  <p className="text-[#94a3b8] text-xs mb-1">6 Saat Sonra</p>
                  <p className="text-2xl font-bold">{waterForecast.predicted_6h}°C</p>
                </div>
                <div className="col-span-2 md:col-span-4 mt-2 flex justify-between text-xs text-[#94a3b8]">
                  <span>Model: RandomForest | Scikit-learn</span>
                  <span className="text-[#22c55e]">Dəqiqlik: {(waterForecast.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ) : (
              <p className="text-[#94a3b8]">Data gözlənilir...</p>
            )}
          </div>
        </div>

        {/* QRAFİKLƏR VƏ XƏBƏRDARLIQLAR */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="glass p-6 rounded-2xl col-span-1 lg:col-span-2">
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
              {[
                {id: 'water_temp', label: 'Su Temperaturu'},
                {id: 'water_level', label: 'Su Səviyyəsi'},
                {id: 'air_temp', label: 'Hava Temp'},
                {id: 'humidity', label: 'Rütubət'}
              ].map(t => (
                <button 
                  key={t.id} 
                  onClick={() => setTab(t.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${tab === t.id ? 'bg-[#38bdf8] text-[#030f1a]' : 'bg-[#0a1628] text-[#94a3b8] hover:bg-[#38bdf8]/20 hover:text-white'}`}>
                  {t.label}
                </button>
              ))}
            </div>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorMain" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.5}/>
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" vertical={false} />
                  <XAxis dataKey="time" stroke="#94a3b8" tick={{fontSize: 12}} tickLine={false} />
                  <YAxis stroke="#94a3b8" tick={{fontSize: 12}} tickLine={false} />
                  <Tooltip contentStyle={{backgroundColor: '#0a1628', borderColor: '#1e3a5f'}} itemStyle={{color: '#38bdf8'}} />
                  <Area type="monotone" dataKey={tab} stroke="#38bdf8" strokeWidth={3} fillOpacity={1} fill="url(#colorMain)" animationDuration={1000} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass p-6 rounded-2xl flex flex-col gap-4">
            <h3 className="text-lg font-bold text-white">🔔 Xəbərdarlıqlar</h3>
            <div className="flex-1 overflow-y-auto pr-2 space-y-3">
              {alerts.length > 0 ? alerts.map(a => (
                <div key={a.id} className={`p-4 rounded-xl border ${a.severity === 'critical' ? 'bg-[#ef4444]/10 border-[#ef4444]/50' : a.severity === 'warning' ? 'bg-[#f59e0b]/10 border-[#f59e0b]/50' : 'bg-[#38bdf8]/10 border-[#38bdf8]/50'}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-white font-medium">{a.message}</p>
                      <p className="text-xs text-[#94a3b8] mt-1">{new Date(a.timestamp).toLocaleTimeString('az-AZ')} | {a.sensor}</p>
                    </div>
                    <button onClick={() => handleResolveAlert(a.id)} className="text-xs px-3 py-1 bg-black/30 rounded border border-white/10 hover:bg-white/10 transition">Bağla</button>
                  </div>
                </div>
              )) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 bg-[#22c55e]/10 border border-[#22c55e]/20 rounded-xl glow-green">
                  <span className="text-4xl mb-2">✓</span>
                  <p className="text-[#22c55e] font-medium">Bütün parametrlər normaldır</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* SYSTEM STATUS PANEL */}
        <div className="glass p-6 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <div className="relative w-20 h-20 flex items-center justify-center rounded-full bg-[#0a1628] border-4" style={{borderColor: systemStatus?.score >= 70 ? '#22c55e' : systemStatus?.score >= 40 ? '#f59e0b' : '#ef4444'}}>
              <span className="text-2xl font-bold">{systemStatus?.score || 0}</span>
            </div>
            <div>
              <h4 className="text-xl font-bold">{systemStatus?.summary || 'Sistem Analiz Edilir...'}</h4>
              <p className="text-sm text-[#94a3b8] mt-1">Sistem İndeksi (0-100)</p>
            </div>
          </div>
          <div className="flex gap-4 flex-wrap justify-center">
            {['Arduino', 'DS18B20', 'HC-SR04', 'DHT11'].map(hw => (
              <div key={hw} className="flex items-center gap-2 bg-[#0a1628] px-3 py-1.5 rounded-lg border border-[#38bdf8]/20">
                <span className="w-2 h-2 rounded-full bg-[#f59e0b]"></span>
                <span className="text-xs text-[#94a3b8]">{hw}</span>
              </div>
            ))}
            <p className="w-full text-center text-xs text-[#f59e0b] mt-2">Mock Rejim (Hardware qoşulduqda avtomatik keçid olacaq)</p>
          </div>
        </div>

        {/* FOOTER */}
        <footer className="text-center text-[#94a3b8] text-sm py-4 border-t border-[#1e3a5f]">
          <p>AquaMind AI v2.0 — Azərbaycan Respublikası, Bakı 2024</p>
          <p className="text-xs mt-1">Powered by FastAPI · MySQL · Next.js · Scikit-learn</p>
        </footer>

      </div>
    </div>
  );
}

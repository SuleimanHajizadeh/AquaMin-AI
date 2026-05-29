# --- Simulyasiya parametrləri ---
temperature = 25     # °C
pH = 6.5
nitrate = 30         # ppm

# --- Optimal baza (JSON kimi) ---
optimal_conditions = {
    "temp": 25,
    "pH": 6.5,
    "gros_factor": 10
}

# --- Gros faktor hesablayan funksiya ---
def gros_factor(temp, pH):
    if temp == optimal_conditions["temp"] and pH == optimal_conditions["pH"]:
        return 10
    # Sadə nümunə: ±1 dərəcə və pH fərqi azaldır gros faktoru
    diff = abs(temp - optimal_conditions["temp"]) + abs(pH - optimal_conditions["pH"])
    return max(10 - int(diff*2), 0)  # Minimum 0

# --- Tənzimləmə funksiyası ---
def optimize_gros(target):
    # Bu sadə nümunədə target üçün təxmini temp və pH çıxarılır
    if target >= 10:
        return optimal_conditions["temp"], optimal_conditions["pH"]
    else:
        temp = optimal_conditions["temp"] - (10 - target)/2
        pH = optimal_conditions["pH"] + (10 - target)/2
        return round(temp,1), round(pH,2)

# --- Siqnalizasiya ---
def check_alert(temp, pH):
    if temp < 20 or temp > 30 or pH < 6 or pH > 8:
        return "Diqqət! Optimal aralıqdan çıxılıb."
    else:
        return "Parametrlər normaldır."

# --- Simulyasiya çıxışı ---
current_gros = gros_factor(temperature, pH)
alert = check_alert(temperature, pH)
optimal_temp, optimal_pH = optimize_gros(8)

print("Simulyasiya dəyərləri:")
print(f"Temperatur: {temperature} °C, pH: {pH}, Nitrat: {nitrate} ppm")
print(f"Gros faktor: {current_gros}/10")
print(f"Alert: {alert}")
print(f"Gros 8 üçün təxmini optimal: Temperatur={optimal_temp}, pH={optimal_pH}")


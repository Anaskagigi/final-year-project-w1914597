import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# date range
start_date = datetime(2019, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date)

# empty lists
temperatures = []
precipitations = []
wind_speeds = []
weather_conditions = []

# Transport modes
modes = ["Underground", "Bus", "Overground", "Tram", "DLR", "National Rail"]
delays = {mode: [] for mode in modes}
cancellations = {mode: [] for mode in modes}
riderships = {mode: [] for mode in modes}

# Simulating the data
for date in date_range:
    # Simulate temperature based on month
    if date.month in [12, 1, 2]:  # Winter
        temp = round(np.random.uniform(-10, 5))
    elif date.month in [3, 4, 5]:  # Spring
        temp = round(np.random.uniform(5, 20))
    elif date.month in [6, 7, 8]:  # Summer
        temp = round(np.random.uniform(20, 35))
    else:  # Fall
        temp = round(np.random.uniform(10, 25))
    
    # Simulate precipitation
    precip = round(np.random.uniform(0, 20)) if np.random.rand() < 0.3 else 0
    
    # Simulate wind speed
    wind = round(np.random.uniform(5, 30))
    
    # Simulate weather condition
    if precip > 15:
        condition = "Thunderstorm"
    elif precip > 10:
        condition = "Heavy Rain" if temp > 0 else "Heavy Snow"
    elif precip > 5:
        condition = "Light Rain" if temp > 0 else "Light Snow"
    elif temp < 0:
        condition = "Clear" if np.random.rand() < 0.8 else "Light Snow"
    else:
        condition = "Clear" if np.random.rand() < 0.7 else "Partly Cloudy"
    
    # Simulate transport metrics
    for mode in modes:
        if condition == "Heavy Snow":
            delay = round(np.random.uniform(20, 35)) if mode != "Underground" else round(np.random.uniform(10, 20))
            cancel = round(np.random.uniform(8, 15)) if mode != "Underground" else round(np.random.uniform(2, 5))
            ridership = round(np.random.uniform(50, 150)) if mode != "Underground" else round(np.random.uniform(150, 200))
        elif condition == "Thunderstorm":
            delay = round(np.random.uniform(10, 20)) if mode != "Underground" else round(np.random.uniform(5, 10))
            cancel = round(np.random.uniform(3, 8)) if mode != "Underground" else round(np.random.uniform(1, 3))
            ridership = round(np.random.uniform(70, 120)) if mode != "Underground" else round(np.random.uniform(200, 250))
        elif condition == "Light Snow" or condition == "Heavy Rain":
            delay = round(np.random.uniform(10, 20)) if mode != "Underground" else round(np.random.uniform(5, 10))
            cancel = round(np.random.uniform(4, 8)) if mode != "Underground" else round(np.random.uniform(1, 3))
            ridership = round(np.random.uniform(80, 130)) if mode != "Underground" else round(np.random.uniform(220, 280))
        elif condition == "Light Rain":
            delay = round(np.random.uniform(5, 10)) if mode != "Underground" else round(np.random.uniform(2, 5))
            cancel = round(np.random.uniform(2, 5)) if mode != "Underground" else round(np.random.uniform(0, 2))
            ridership = round(np.random.uniform(90, 140)) if mode != "Underground" else round(np.random.uniform(250, 300))
        else:  # Clear or Partly Cloudy
            delay = round(np.random.uniform(1, 5)) if mode != "Underground" else round(np.random.uniform(1, 3))
            cancel = round(np.random.uniform(0, 2)) if mode != "Underground" else round(np.random.uniform(0, 1))
            ridership = round(np.random.uniform(100, 150)) if mode != "Underground" else round(np.random.uniform(280, 320))
        
        # Append to lists
        delays[mode].append(delay)
        cancellations[mode].append(cancel)
        riderships[mode].append(ridership)
    
    # Append weather data
    temperatures.append(temp)
    precipitations.append(precip)
    wind_speeds.append(wind)
    weather_conditions.append(condition)

# Creating DataFrame
data = {
    "Date": date_range,
    "Temperature (°C)": temperatures,
    "Precipitation (mm)": precipitations,
    "Wind Speed (km/h)": wind_speeds,
    "Weather Condition": weather_conditions
}

for mode in modes:
    data[f"{mode} Delays (min)"] = delays[mode]
    data[f"{mode} Cancellations (%)"] = cancellations[mode]
    data[f"{mode} Ridership (thousands)"] = riderships[mode]

df = pd.DataFrame(data)

# saving the data into CSV
df.to_csv("london_transport_weather_2019_2024.csv", index=False)

print("Dataset generated successfully!")

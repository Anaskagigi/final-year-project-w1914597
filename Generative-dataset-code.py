import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Setting random seed for reproducibility
np.random.seed(42)

# Date range
start_date = datetime(2019, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date)

# Empty lists
temperatures = []
precipitations = []
wind_speeds = []
weather_conditions = []

# Transport modes
modes = ["Underground", "Bus", "Overground", "Tram", "DLR", "National Rail"]
delays = {mode: [] for mode in modes}
cancellations = {mode: [] for mode in modes}
riderships = {mode: [] for mode in modes}

# Setting base monthly average temperatures (°C) for London
monthly_avg_temp = {
    1: 5, 2: 6, 3: 9, 4: 12, 5: 16, 6: 19,
    7: 22, 8: 21, 9: 18, 10: 14, 11: 9, 12: 6
}

# Setting base monthly average precipitation (mm)
monthly_avg_precip = {
    1: 55, 2: 40, 3: 45, 4: 40, 5: 45, 6: 35,
    7: 40, 8: 45, 9: 50, 10: 65, 11: 70, 12: 65
}

# Simulating the data
previous_temp = 10  # the starting temperature

for date in date_range:
    # Smooth temperature fluctuation around the monthly average
    base_temp = monthly_avg_temp[date.month]
    temp = previous_temp + np.random.uniform(-2, 2)  # small daily fluctuation
    temp = temp * 0.7 + base_temp * 0.3  # drift slowly toward the monthly average
    temp = round(temp, 1)
    previous_temp = temp

    # Precipitation with some randomness
    avg_precip = monthly_avg_precip[date.month]
    precip_chance = 0.4 if avg_precip > 50 else 0.2  
    precip = round(np.random.uniform(0, avg_precip)) if np.random.rand() < precip_chance else 0

    # Wind speed 
    if date.month in [11, 12, 1, 2]:
        wind = round(np.random.uniform(15, 35))
    else:
        wind = round(np.random.uniform(5, 25))

    # Determining the weather condition
    if precip > 20:
        condition = "Thunderstorm"
    elif precip > 10:
        condition = "Heavy Rain" if temp > 0 else "Heavy Snow"
    elif precip > 2:
        condition = "Light Rain" if temp > 0 else "Light Snow"
    else:
        if temp < 3:
            condition = "Frosty" if np.random.rand() < 0.7 else "Clear"
        else:
            condition = "Clear" if np.random.rand() < 0.7 else "Partly Cloudy"

    # Transport simulation 
    for mode in modes:
        if condition in ["Heavy Snow", "Thunderstorm"]:
            delay = round(np.random.uniform(20, 35)) if mode != "Underground" else round(np.random.uniform(10, 20))
            cancel = round(np.random.uniform(8, 15)) if mode != "Underground" else round(np.random.uniform(2, 5))
            ridership = round(np.random.uniform(50, 150)) if mode != "Underground" else round(np.random.uniform(150, 200))
        elif condition in ["Light Snow", "Heavy Rain"]:
            delay = round(np.random.uniform(10, 20)) if mode != "Underground" else round(np.random.uniform(5, 10))
            cancel = round(np.random.uniform(4, 8)) if mode != "Underground" else round(np.random.uniform(1, 3))
            ridership = round(np.random.uniform(80, 130)) if mode != "Underground" else round(np.random.uniform(220, 280))
        elif condition == "Light Rain":
            delay = round(np.random.uniform(5, 10)) if mode != "Underground" else round(np.random.uniform(2, 5))
            cancel = round(np.random.uniform(2, 5)) if mode != "Underground" else round(np.random.uniform(0, 2))
            ridership = round(np.random.uniform(90, 140)) if mode != "Underground" else round(np.random.uniform(250, 300))
        else:  # Clear, Partly Cloudy, Frosty
            delay = round(np.random.uniform(1, 5)) if mode != "Underground" else round(np.random.uniform(1, 3))
            cancel = round(np.random.uniform(0, 2)) if mode != "Underground" else round(np.random.uniform(0, 1))
            ridership = round(np.random.uniform(100, 150)) if mode != "Underground" else round(np.random.uniform(280, 320))

        delays[mode].append(delay)
        cancellations[mode].append(cancel)
        riderships[mode].append(ridership)

    # Append for weather data
    temperatures.append(temp)
    precipitations.append(precip)
    wind_speeds.append(wind)
    weather_conditions.append(condition)

# Creating a DataFrame
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

# Saving the data into CSV
df.to_csv("london_transport_weather_2019_2024_New.csv", index=False)

print("Improved dataset generated successfully!")

Impact of Weather on Public Transport in London
Overview
This project investigates how different weather conditions impact public transport services in London, focusing on ridership patterns, delays, cancellations, and overall service reliability. The study integrates weather data (temperature, precipitation, wind speed, snowfall) with transport data (bus, Underground, Overground, Tram, DLR, and National Rail ridership) to identify patterns and correlations.

The primary objectives are:

Analyze ridership fluctuations under different weather conditions.
Examine how severe weather affects delays and cancellations.
Provide recommendations for improving TfL’s operational strategies.
An interactive Streamlit dashboard has been created to visualize key trends and correlations, providing an accessible tool for transport decision-making.

Features
Interactive Filters : Select weather conditions, transport modes, and years to filter data dynamically.
Key Metrics : Display average delays, cancellations, and ridership for selected filters.
Visualizations :
Bar charts showing average delays by transport mode.
Box plots illustrating the distribution of delays and cancellations.
Stacked bar charts comparing total delays and cancellations across modes.
Scatter plots examining the relationship between weather variables and performance metrics.
Heatmaps visualizing daily delays over time.
Pie charts showing the proportion of ridership across transport modes.
Decision Tree : Predict delays based on weather variables using a simple decision tree model.
Dataset
Due to the lack of sufficient publicly available real-world data, a synthetic dataset was generated to simulate realistic interactions between weather conditions and transport performance metrics. The dataset includes:

Weather variables: Temperature (°C), Precipitation (mm), Wind Speed (km/h), Snowfall (cm).
Transport metrics: Delays (min), Cancellations (%), Ridership (thousands) for various transport modes.
The dataset is stored in data/london_transport_weather_2019_2024_rounded.csv.

Installation and Setup
To run this project locally, follow these steps:

Prerequisites
Python 3.8 or higher
Pip (Python package manager)
Steps
Clone the repository:

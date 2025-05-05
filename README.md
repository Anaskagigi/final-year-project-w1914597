
# **Impact of Weather on Public Transport in London**

## **Overview**:
This project investigates how different weather conditions impact public transport services in London, focusing on ridership patterns, delays, cancellations, and overall service reliability. The study integrates weather data (temperature, precipitation, wind speed, snowfall) with transport data (bus, Underground, Overground, Tram, DLR, and National Rail ridership) to identify patterns and correlations.

The primary objectives are:
1. Analyze ridership fluctuations under different weather conditions.
2. Examine how severe weather affects delays and cancellations.
3. Provide recommendations for improving TfL’s operational strategies.

An interactive **Streamlit** dashboard has been created to visualize key trends and correlations, providing an accessible tool for transport decision-making.

## **Features**:

- **Interactive Filters**: Select weather conditions, transport modes, and years to filter data dynamically.
- **Key Metrics**: Display average delays, cancellations, and ridership for selected filters.
- **Visualizations**:
  - Bar charts showing average delays by transport mode.
  - Box plots illustrating the distribution of delays and cancellations.
  - Stacked bar charts comparing total delays and cancellations across modes.
  - Scatter plots examining the relationship between weather variables and performance metrics.
  - Heatmaps visualizing daily delays over time.
  - Pie charts showing the proportion of ridership across transport modes.
  
- **Decision Tree**: Predict delays based on weather variables using a simple decision tree model.

## **Dataset**:
Due to the lack of sufficient publicly available real-world data, a **synthetic dataset** was generated to simulate realistic interactions between weather conditions and transport performance metrics. The dataset includes:

- **Weather Variables**:
  - Temperature (°C)
  - Precipitation (mm)
  - Wind Speed (km/h)
  - Snowfall (cm)
  
- **Transport Metrics**:
  - Delays (min)
  - Cancellations (%)
  - Ridership (thousands) for various transport modes.

The dataset is stored in `data/london_transport_weather_2019_2024_NEW.csv`.

## **Installation and Setup**:
To run this project locally, follow these steps:

### **Prerequisites**:
- Python 3.8 or higher
- Pip (Python package manager)

### **Steps**:
1. Clone the repository:
    ```bash
    git clone https://github.com/Anaskagigi/final-year-project_w191459.git
    cd final-year-project_w191459
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```bash
    streamlit run streamlit_app.py
    ```

4. Open the app in your browser at [http://localhost:8501](http://localhost:8501).

## **File Structure**:
```plaintext
final-year-project_w1914597/
│
├── data/
│   └── london_transport_weather_2019_2024_NEW.csv  # Dataset
├── streamlit_app.py  # Main Streamlit application script
├── requirements.txt  # List of Python dependencies
└── README.md  # This file
```

## **Usage**:
- Use the sidebar to select weather conditions, transport modes, and years.
- Explore the visualizations and insights provided in the dashboard.
- Use the decision tree section to predict delays based on input weather variables.


## **Acknowledgments**:
- **Supervisor**: Rolf Banziger
- **University**: University of Westminster, School of Computer Science & Engineering
- **Tools and Libraries**:
  - Streamlit
  - Pandas
  - NumPy
  - Plotly
  - Scikit-learn

## **Contact**:

- GitHub: [@Anaskagigi](https://github.com/Anaskagigi)
- Email: [w1914597@my.westminster.ac.uk]

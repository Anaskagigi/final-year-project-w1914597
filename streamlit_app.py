import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Set page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Load the data safely
@st.cache_data
def load_data():
    data = pd.read_csv("data/london_transport_weather_2019_2024_NEW.csv")
    data['Date'] = pd.to_datetime(data['Date'], dayfirst=True, errors='coerce')  # Safe parsing
    data = data.dropna(subset=['Date'])  # Drop rows where Date failed to parse
    data['Year'] = data['Date'].dt.year
    return data

data = load_data()

# Sidebar selections
st.sidebar.title("Impact of Weather on Public Transport Dashboard")
st.sidebar.markdown("Explore how weather affects London's public transport system.")

# Session states
if 'selected_conditions' not in st.session_state:
    st.session_state.selected_conditions = []
if 'selected_modes' not in st.session_state:
    st.session_state.selected_modes = []
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = []

# Multi-selects
weather_conditions = data["Weather Condition"].unique()
selected_conditions = st.sidebar.multiselect(
    "Select Weather Conditions", options=weather_conditions, default=st.session_state.selected_conditions
)

transport_modes = ["Underground", "Bus", "Overground", "Tram", "DLR", "National Rail"]
selected_modes = st.sidebar.multiselect(
    "Select Transport Modes", options=transport_modes, default=st.session_state.selected_modes
)

available_years = sorted(data['Year'].unique())
selected_years = st.sidebar.multiselect(
    "Select Years", options=available_years, default=st.session_state.selected_years
)

# Save selections
st.session_state.selected_conditions = selected_conditions
st.session_state.selected_modes = selected_modes
st.session_state.selected_years = selected_years

# Filter the dataset
filtered_data = data[
    (data["Weather Condition"].isin(selected_conditions)) &
    (data["Year"].isin(selected_years))
]

# Dashboard Title
st.title("Impact of Weather on London's Public Transport")

st.markdown("""
This dashboard analyzes how different weather conditions affect delays, cancellations, and ridership across London's public transport modes.
""")

# Main dashboard
if not selected_conditions or not selected_modes or not selected_years:
    st.warning("Please select at least one weather condition, one transport mode, and one year.")
else:
    # Key Metrics Section
    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)

    avg_delays = filtered_data[[f"{mode} Delays (min)" for mode in selected_modes]].mean().round(1)
    avg_cancellations = filtered_data[[f"{mode} Cancellations (%)" for mode in selected_modes]].mean().round(1)
    avg_ridership = filtered_data[[f"{mode} Ridership (thousands)" for mode in selected_modes]].mean().round(1)

    with col1:
        st.metric("Max Avg Delay (min)", f"{avg_delays.max()} min", delta=f"{avg_delays.idxmax().split(' ')[0]}")
    with col2:
        st.metric("Max Avg Cancellation (%)", f"{avg_cancellations.max()}%", delta=f"{avg_cancellations.idxmax().split(' ')[0]}")
    with col3:
        st.metric("Max Avg Ridership (k)", f"{int(avg_ridership.max())}k", delta=f"{avg_ridership.idxmax().split(' ')[0]}")

    # Visualizations Section
    st.header("Visualizations")

    # Bar Chart: Average Delays
    st.subheader("Average Delays by Mode")
    fig = px.bar(
        x=avg_delays.index,
        y=avg_delays.values,
        labels={"x": "Mode", "y": "Avg Delay (min)"},
        color=avg_delays.values,
        color_continuous_scale="Viridis",
        title="Average Delays by Mode"
    )
    st.plotly_chart(fig)

    # Box Plot: Delay Distribution
    st.subheader("Delay Distribution Across Modes")
    fig = go.Figure()
    for mode in selected_modes:
        fig.add_trace(go.Box(y=filtered_data[f"{mode} Delays (min)"], name=mode))
    fig.update_layout(title="Delay Distribution by Mode", yaxis_title="Delays (min)")
    st.plotly_chart(fig)

    # Stacked Bar Chart: Total Delays and Cancellations
    st.subheader("Total Delays and Cancellations")
    total_delays = filtered_data[[f"{mode} Delays (min)" for mode in selected_modes]].sum()
    total_cancellations = filtered_data[[f"{mode} Cancellations (%)" for mode in selected_modes]].sum()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=selected_modes, y=total_delays.values, name="Total Delays"))
    fig.add_trace(go.Bar(x=selected_modes, y=total_cancellations.values, name="Total Cancellations"))
    fig.update_layout(barmode='stack', title="Total Delays and Cancellations")
    st.plotly_chart(fig)

    # Scatter Plot: Precipitation vs Delays
    st.subheader("Impact of Precipitation on Delays")
    scatter_data = filtered_data.melt(
        id_vars=["Temperature (°C)", "Precipitation (mm)", "Wind Speed (km/h)"],
        value_vars=[f"{mode} Delays (min)" for mode in selected_modes],
        var_name="Mode", value_name="Delay"
    )
    fig = px.scatter(
        scatter_data,
        x="Precipitation (mm)",
        y="Delay",
        color="Mode",
        title="Precipitation vs Delay"
    )
    st.plotly_chart(fig)

    # Heatmap: Daily Delays
    st.subheader("Daily Delays Heatmap")
    heatmap_data = filtered_data.groupby(["Date"])[[f"{mode} Delays (min)" for mode in selected_modes]].mean().T
    fig = px.imshow(
        heatmap_data,
        labels=dict(x="Date", y="Mode", color="Avg Delay"),
        title="Daily Delay Heatmap"
    )
    st.plotly_chart(fig)

    # Pie Chart: Ridership
    st.subheader("Ridership Distribution")
    ridership_total = filtered_data[[f"{mode} Ridership (thousands)" for mode in selected_modes]].sum()
    fig = px.pie(
        names=ridership_total.index,
        values=ridership_total.values,
        title="Ridership Distribution Across Modes"
    )
    st.plotly_chart(fig)

    # Download filtered data
    st.subheader("Download Filtered Data")
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="filtered_transport_weather_data.csv",
        mime="text/csv"
    )

# =====================
# Prediction Section
# =====================

st.header("Predict Delays Based on Weather Conditions")

@st.cache_resource
def train_model_and_evaluate(mode):
    features = ["Temperature (°C)", "Precipitation (mm)", "Wind Speed (km/h)"]
    if "Snowfall (cm)" in data.columns:
        features.append("Snowfall (cm)")
    X = data[features]
    y = data[f"{mode} Delays (min)"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = DecisionTreeRegressor(max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    return model, features, r2, mae, rmse

if selected_modes:
    selected_mode = selected_modes[0]
    model, features, r2, mae, rmse = train_model_and_evaluate(selected_mode)

    st.subheader(f"Prediction Model Evaluation for {selected_mode}")
    st.markdown(f"""
    - **R² Score**: {r2:.2f} (higher is better, closer to 1.0)
    - **Mean Absolute Error (MAE)**: {mae:.2f} minutes
    - **Root Mean Squared Error (RMSE)**: {rmse:.2f} minutes
    """)

    st.subheader(f"Predict Delay for {selected_mode}")

    temperature = st.number_input("Temperature (°C)", value=15.0)
    precipitation = st.number_input("Precipitation (mm)", value=0.0)
    wind_speed = st.number_input("Wind Speed (km/h)", value=10.0)
    input_values = [temperature, precipitation, wind_speed]

    if "Snowfall (cm)" in data.columns:
        snowfall = st.number_input("Snowfall (cm)", value=0.0)
        input_values.append(snowfall)

    if st.button("Predict Delay"):
        prediction = model.predict([input_values])
        st.success(f"Predicted Delay: {prediction[0]:.1f} minutes")

# Footer
st.markdown("---")
st.markdown("Developed by [Anas Kagigi](https://github.com/Anaskagigi/final-year-project-w1914597)")

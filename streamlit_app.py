import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn import tree
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Load data
@st.cache_data  # Use @st.cache if using an older version of Streamlit
def load_data():
    return pd.read_csv("data/london_transport_weather_2019_2024.csv")

data = load_data()

# Sidebar for user inputs
st.sidebar.title("Public Transport Weather Impact Dashboard")
st.sidebar.markdown("Explore how weather affects London's public transport.")

# Reset selections on rerun
if 'selected_conditions' not in st.session_state:
    st.session_state.selected_conditions = []
if 'selected_modes' not in st.session_state:
    st.session_state.selected_modes = []
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = []

# Multi-select for weather conditions
weather_conditions = data["Weather Condition"].unique()
selected_conditions = st.sidebar.multiselect(
    "Select Weather Conditions", 
    options=weather_conditions,
    default=st.session_state.selected_conditions
)

# Multi-select for transport modes
transport_modes = ["Underground", "Bus", "Overground", "Tram", "DLR", "National Rail"]
selected_modes = st.sidebar.multiselect(
    "Select Transport Modes", 
    options=transport_modes,
    default=st.session_state.selected_modes
)

# Multi-select for years
data['Year'] = pd.to_datetime(data['Date']).dt.year  # Extract year from Date column
available_years = sorted(data['Year'].unique())
selected_years = st.sidebar.multiselect(
    "Select Years", 
    options=available_years,
    default=st.session_state.selected_years
)

# Save selections to session state
st.session_state.selected_conditions = selected_conditions
st.session_state.selected_modes = selected_modes
st.session_state.selected_years = selected_years

# Filter data based on selected weather conditions, transport modes, and years
filtered_data = data[
    (data["Weather Condition"].isin(selected_conditions)) &
    (data['Year'].isin(selected_years))
]

# Title and Introduction
st.title("Impact of Weather on London's Public Transport")
st.markdown("""
This dashboard analyzes how different weather conditions affect delays, cancellations, and ridership across London's public transport modes.
""")

# Handle empty selections
if not selected_conditions or not selected_modes or not selected_years:
    st.warning("Please select at least one weather condition, one transport mode, and one year from the sidebar to proceed.")
else:
    # Section 1: Key Metrics
    st.header(f"Key Metrics for Selected Conditions, Modes, and Years")
    col1, col2, col3 = st.columns(3)

    # Calculate average delays, cancellations, and ridership for selected transport modes
    avg_delays = filtered_data[[f"{mode} Delays (min)" for mode in selected_modes]].mean().round(1)
    avg_cancellations = filtered_data[[f"{mode} Cancellations (%)" for mode in selected_modes]].mean().round(1)
    avg_ridership = filtered_data[[f"{mode} Ridership (thousands)" for mode in selected_modes]].mean().round(1)

    with col1:
        st.metric("Average Delays (min)", f"{avg_delays.max()} min", delta=f"{avg_delays.idxmax().split(' ')[0]} worst affected")
    with col2:
        st.metric("Average Cancellations (%)", f"{avg_cancellations.max()}%", delta=f"{avg_cancellations.idxmax().split(' ')[0]} worst affected")
    with col3:
        st.metric("Average Ridership (thousands)", f"{int(avg_ridership.max())}k", delta=f"{avg_ridership.idxmax().split(' ')[0]} highest ridership")

    # Section 2: Visualizations
    st.header("Visualizations")

    # Bar Chart: Average Delays by Transport Mode
    st.subheader("Average Delays by Transport Mode")
    fig = px.bar(
        x=avg_delays.index,
        y=avg_delays.values,
        labels={"x": "Transport Mode", "y": "Average Delays (min)"},
        title="Average Delays by Transport Mode",
        color=avg_delays.values,
        color_continuous_scale="Viridis"
    )
    fig.update_traces(hovertemplate="Transport Mode: %{x}<br>Average Delay: %{y} min<extra></extra>")
    st.plotly_chart(fig)

    # Box Plot: Distribution of Delays and Cancellations
    st.subheader("Distribution of Delays and Cancellations")
    delays_columns = [f"{mode} Delays (min)" for mode in selected_modes]
    cancellations_columns = [f"{mode} Cancellations (%)" for mode in selected_modes]

    fig = go.Figure()
    for i, col in enumerate(delays_columns):
        fig.add_trace(go.Box(y=filtered_data[col], name=col.split(" ")[0], marker_color=px.colors.sequential.Plasma[i % len(px.colors.sequential.Plasma)]))
    fig.update_layout(title="Distribution of Delays Across Transport Modes", yaxis_title="Delays (min)")
    st.plotly_chart(fig)

    # Section 3: Prediction Model
    st.header("Predict Delays Based on Weather Conditions")
    st.markdown("""
    Use the decision tree model below to predict delays based on weather variables such as temperature, precipitation, wind speed, and snowfall.
    """)

    # Train a Decision Tree model for prediction
    @st.cache_resource  # Use @st.cache if using an older version of Streamlit
    def train_decision_tree(mode):
        features = ["Temperature (°C)", "Precipitation (mm)", "Wind Speed (km/h)"]
        
        # Check if 'Snowfall (cm)' exists in the dataset
        if "Snowfall (cm)" in data.columns:
            features.append("Snowfall (cm)")
        
        target = f"{mode} Delays (min)"
        X = data[features]
        y = data[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = DecisionTreeRegressor(random_state=42, max_depth=3)  # Limit depth for simplicity
        model.fit(X_train, y_train)
        return model, features  # Return both the model and the features list

    if selected_modes:
        selected_mode = selected_modes[0]  # Use the first selected mode for prediction
        model, features = train_decision_tree(selected_mode)  # Get both the model and features

        # Display the decision tree rules as text
        st.subheader("Decision Tree Rules")
        tree_rules = export_text(model, feature_names=features)
        st.text(tree_rules)

        # Input fields for weather variables
        st.subheader(f"Predict Delays for {selected_mode}")
        temperature = st.number_input("Temperature (°C)", value=15.0)
        precipitation = st.number_input("Precipitation (mm)", value=0.0)
        wind_speed = st.number_input("Wind Speed (km/h)", value=10.0)
        snowfall = st.number_input("Snowfall (cm)", value=0.0, disabled="Snowfall (cm)" not in data.columns)

        # Predict button
        if st.button("Predict"):
            input_data = [[temperature, precipitation, wind_speed]]
            
            # Include snowfall if it exists in the dataset
            if "Snowfall (cm)" in data.columns:
                input_data[0].append(snowfall)
            
            prediction = model.predict(input_data)
            st.success(f"Predicted Delay: {prediction[0]:.1f} minutes")
    else:
        st.warning("Please select at least one transport mode from the sidebar to proceed with predictions.")

# Footer
st.markdown("---")
st.markdown("Developed by [Anas Kagigi](https://github.com/Anaskagigi/final-year-project_w191459).")

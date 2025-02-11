import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Load data
@st.cache
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
    st.markdown("""
    This bar chart shows the average delays (in minutes) experienced by each selected transport mode under the chosen weather conditions and years. 
    The color gradient highlights the severity of delays, with darker colors indicating higher delays. 
    Surface modes like buses and trams are typically more affected by adverse weather compared to underground services.
    """)

    # Box Plot: Distribution of Delays and Cancellations
    st.subheader("Distribution of Delays and Cancellations")
    delays_columns = [f"{mode} Delays (min)" for mode in selected_modes]
    cancellations_columns = [f"{mode} Cancellations (%)" for mode in selected_modes]

    fig = go.Figure()
    for i, col in enumerate(delays_columns):
        fig.add_trace(go.Box(y=filtered_data[col], name=col.split(" ")[0], marker_color=px.colors.sequential.Plasma[i % len(px.colors.sequential.Plasma)]))
    fig.update_layout(title="Distribution of Delays Across Transport Modes", yaxis_title="Delays (min)")
    st.plotly_chart(fig)
    st.markdown("""
    This box plot visualizes the distribution of delays for each transport mode, highlighting variability and outliers. 
    The boxes represent the interquartile range (IQR), while the whiskers show the range of typical values. 
    Extreme outliers (points outside the whiskers) indicate unusual delays caused by severe weather events.
    """)

    # Stacked Bar Chart: Total Delays and Cancellations Across Modes
    st.subheader("Total Delays and Cancellations Across Transport Modes")
    total_delays = filtered_data[delays_columns].sum().reset_index()
    total_delays.columns = ["Mode", "Total Delays"]
    total_cancellations = filtered_data[cancellations_columns].sum().reset_index()
    total_cancellations.columns = ["Mode", "Total Cancellations"]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=total_delays["Mode"], y=total_delays["Total Delays"], name="Total Delays", marker_color=px.colors.sequential.Inferno[0]))
    fig.add_trace(go.Bar(x=total_cancellations["Mode"], y=total_cancellations["Total Cancellations"], name="Total Cancellations", marker_color=px.colors.sequential.Inferno[2]))
    fig.update_layout(barmode="stack", title="Total Delays and Cancellations Across Transport Modes")
    st.plotly_chart(fig)
    st.markdown("""
    This stacked bar chart compares the total delays and cancellations across all selected transport modes. 
    Each bar represents a transport mode, with delays shown in one color and cancellations in another. 
    This visualization helps identify which modes are most disrupted by the selected weather conditions.
    """)

    # Scatter Plot: Weather Variables vs. Performance Metrics
    st.subheader("Weather Variables vs. Performance Metrics")
    scatter_data = filtered_data.melt(
        id_vars=["Temperature (°C)", "Precipitation (mm)", "Wind Speed (km/h)"],
        value_vars=[f"{mode} Delays (min)" for mode in selected_modes],
        var_name="Transport Mode", value_name="Delays"
    )
    fig = px.scatter(
        scatter_data,
        x="Precipitation (mm)",
        y="Delays",
        color="Transport Mode",
        title="Impact of Precipitation on Delays",
        labels={"Precipitation (mm)": "Precipitation (mm)", "Delays": "Delays (min)"},
        color_discrete_sequence=px.colors.sequential.Magma
    )
    fig.update_traces(marker=dict(size=8), selector=dict(mode="markers"))
    st.plotly_chart(fig)
    st.markdown("""
    This scatter plot examines the relationship between precipitation levels and delays for each transport mode. 
    Each point represents a day, with the color indicating the transport mode. 
    A positive trend suggests that higher precipitation leads to increased delays, particularly for surface modes like buses and trams.
    """)

    # Time-Series Heatmap: Daily Delays Over Time
    st.subheader("Daily Delays Over Time")
    heatmap_data = filtered_data.groupby(["Date"])[delays_columns].mean().reset_index()
    heatmap_data.set_index("Date", inplace=True)
    fig = px.imshow(
        heatmap_data.T,
        labels=dict(x="Date", y="Transport Mode", color="Average Delays"),
        title="Daily Delays Across Transport Modes",
        color_continuous_scale="Cividis"
    )
    fig.update_layout(width=800, height=600)
    st.plotly_chart(fig)
    st.markdown("""
    This heatmap visualizes daily delays for each transport mode over time. 
    Darker colors indicate higher delays, while lighter colors represent minimal disruptions. 
    This view helps identify seasonal patterns, such as increased delays during winter months due to snow or ice.
    """)

    # Pie Chart: Proportion of Ridership Across Modes
    st.subheader("Proportion of Ridership Across Transport Modes")
    ridership_columns = [f"{mode} Ridership (thousands)" for mode in selected_modes]
    ridership_data = filtered_data[ridership_columns].sum().reset_index()
    ridership_data.columns = ["Mode", "Total Ridership"]
    fig = px.pie(
        ridership_data,
        names="Mode",
        values="Total Ridership",
        title="Proportion of Ridership Across Transport Modes",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig)
    st.markdown("""
    This pie chart shows the proportion of total ridership across the selected transport modes. 
    It provides insight into which modes are most popular under the chosen weather conditions and years. 
    For example, underground services often see higher ridership during adverse weather due to their resilience.
    """)

    # Section 3: Insights
    st.header("Insights")
    st.markdown("""
    - **Heavy Snow**: Surface transport modes like buses and trams are most affected due to icy roads and reduced visibility.
    - **Thunderstorms**: Trams and DLR experience higher delays due to lightning risks and power outages.
    - **Clear Weather**: Underground services remain largely unaffected, while surface modes see increased ridership.
    """)

    # Explanation for Delays
    st.subheader("Explanation for Delays")
    st.markdown("""
    - **Weather-Related Delays**: Heavy snow and thunderstorms cause significant disruptions due to unsafe road conditions and infrastructure damage.
    - **Infrastructure Issues**: Aging infrastructure is more vulnerable during adverse weather.
    - **Operational Errors**: Human errors and scheduling issues contribute to delays, especially during peak hours.
    """)

    # Section 4: Prediction Model with Decision Tree
    st.header("Predict Delays Based on Weather Conditions")
    st.markdown("""
    Enter weather variables below to predict delays for the selected transport mode during the chosen weather condition.
    """)

    # Train a Decision Tree model for prediction
    @st.cache_resource
    def train_decision_tree(mode):
        features = ["Temperature (°C)", "Precipitation (mm)", "Wind Speed (km/h)"]
        
        # Check if 'Snowfall (cm)' exists in the dataset
        if "Snowfall (cm)" in data.columns:
            features.append("Snowfall (cm)")
        
        target = f"{mode} Delays (min)"
        X = data[features]
        y = data[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = DecisionTreeRegressor(random_state=42, max_depth=5)  # Limit depth for interpretability
        model.fit(X_train, y_train)
        return model, features  # Return both the model and the features list

    if selected_modes:
        selected_mode = selected_modes[0]  # Use the first selected mode for prediction
        model, features = train_decision_tree(selected_mode)  # Get both the model and features

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

        # Visualize the decision tree
        if st.checkbox("Show Decision Tree"):
            fig, ax = plt.subplots(figsize=(20, 10))  # Increase figure size for better readability
            plot_tree(model, feature_names=features, filled=True, fontsize=10, rounded=True, ax=ax)  # Adjust font size and style
            st.pyplot(fig)
    else:
        st.warning("Please select at least one transport mode from the sidebar to proceed with predictions.")

    # Section 5: Download Filtered Data
    if not filtered_data.empty:
        st.subheader("Download Filtered Data")
        st.markdown("""
        You can download the filtered data based on your selections from the sidebar.
        """)
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_transport_weather_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available to download. Please make valid selections in the sidebar.")

# Footer
st.markdown("---")
st.markdown("Developed by [Anas Kagigi](https://github.com/Anaskagigi/final-year-project_w191459).")

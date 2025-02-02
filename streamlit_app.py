import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Load the data
df = pd.read_csv('data/5_Years_Weather_Impact_on_Public_Transport.csv')  # Ensure the correct file path

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Sidebar configuration
st.sidebar.header('Dashboard Controls')

# Sidebar: Select transport types (Bus, Train, etc.)
transport_types = [x for x in df['Public Transport Route'].unique() if x != 'No Service']
selected_transport = st.sidebar.multiselect('Select Transport Type(s)', options=transport_types)

# Sidebar: Select year range (Start and End Year)
start_year = st.sidebar.selectbox('Select Start Year', options=sorted(df['Date'].dt.year.unique()), index=0)
end_year = st.sidebar.selectbox('Select End Year', options=sorted(df['Date'].dt.year.unique()), index=len(df['Date'].dt.year.unique())-1)

# Sidebar: Select weather conditions
weather_conditions = ['Clear', 'Fog', 'Rain', 'Snow', 'Wind', 'Ice']
selected_weather = st.sidebar.multiselect('Select Weather Condition(s)', options=weather_conditions)

# Sidebar: Select Time of Day (Rush Hour / Off-Peak)
time_of_day_options = ['Off-Peak', 'Rush Hour']
selected_time_of_day = st.sidebar.multiselect('Select Time of Day', options=time_of_day_options)

# Ensure the user has selected both year range, transport type(s), weather condition(s), and time of day
if not selected_transport or not start_year or not end_year or not selected_weather or not selected_time_of_day:
    st.markdown(""" 
        # Impact of Weather on Public Transport Dashboard
        Please select the year range, transport type(s), weather condition(s), and time of day from the sidebar to view the data.
    """)
else:
    st.header(f"Impact of Weather on Selected Transport for {start_year} - {end_year}")
    
    # Filter data based on the selected year range, transport type(s), weather condition(s), and time of day
    filtered_df = df[(df['Date'].dt.year >= start_year) & 
                     (df['Date'].dt.year <= end_year) & 
                     df['Public Transport Route'].isin(selected_transport) &
                     df['Weather Condition'].isin(selected_weather)]

    # Filter by Time of Day (Rush Hour / Off-Peak) if only one is selected
    if 'Rush Hour' in selected_time_of_day and 'Off-Peak' not in selected_time_of_day:
        filtered_df = filtered_df[filtered_df['Time of Day'] == 'Rush Hour']
    elif 'Off-Peak' in selected_time_of_day and 'Rush Hour' not in selected_time_of_day:
        filtered_df = filtered_df[filtered_df['Time of Day'] == 'Off-Peak']
    
    # If both Rush Hour and Off-Peak are selected, show all data
    if 'Rush Hour' in selected_time_of_day and 'Off-Peak' in selected_time_of_day:
        pass  # No need to filter, show all data for both time periods

    # Check if the filtered data is empty
    if filtered_df.empty:
        st.warning("No data available for the selected filters. Please adjust your selections.")
    else:
        # Display message with selected filters
        st.markdown(f"### Showing data for: {start_year} to {end_year} and {', '.join(selected_transport)} during {', '.join(selected_weather)} conditions in {', '.join(selected_time_of_day)}.")

        # Key Performance Indicators (KPIs)
        st.subheader('Key Performance Indicators (KPIs)')
        col1, col2, col3, col4 = st.columns(4)

        # Total Delays (minutes)
        total_delays = int(filtered_df['Delay Due to Weather (minutes)'].sum())
        col1.metric("Total Delays (minutes)", f"{total_delays:,}", delta=total_delays)

        # Total Routes Affected
        total_routes = int(filtered_df['Public Transport Route'].nunique())
        col2.metric("Total Routes Affected", total_routes)

        # Average Delay (minutes)
        avg_delay = float(filtered_df['Delay Due to Weather (minutes)'].mean())
        col3.metric("Average Delay (minutes)", f"{avg_delay:.1f}", delta=avg_delay)

        # Average Wind Speed
        avg_wind_speed = filtered_df['Wind Speed (km/h)'].mean()
        col4.metric("Average Wind Speed (km/h)", f"{avg_wind_speed:.1f}")

        # --- Additional KPIs for Weather Conditions ---
        # Average Temperature (°C)
        avg_temperature = filtered_df['Temperature (°C)'].mean()

        # Average Rainfall (mm)
        avg_rainfall = filtered_df['Rainfall (mm)'].mean()

        # Average Humidity (%)
        avg_humidity = filtered_df['Humidity (%)'].mean()

        st.write(f"**Average Temperature (°C):** {avg_temperature:.1f}°C")
        st.write(f"**Average Rainfall (mm):** {avg_rainfall:.1f} mm")
        st.write(f"**Average Humidity (%):** {avg_humidity:.1f}%")

        # --- Visualization Section ---
        st.subheader('Visualizations')

        # Create columns for side-by-side visualization
        col1, col2 = st.columns(2)

        with col1:
            # Heatmap for delays over time (Weekly Data)
            st.write("### Heatmap: Delays Over Time (Weekly)")
            st.write(""" 
                This heatmap shows how weather delays are distributed across weeks and years.
                The values represent the total delays due to weather conditions, categorized by week and year.
            """)
            heatmap_data = filtered_df.pivot_table(values='Delay Due to Weather (minutes)', 
                                                   index=filtered_df['Date'].dt.isocalendar().week, 
                                                   columns=filtered_df['Date'].dt.year, 
                                                   aggfunc=np.sum)
            
            # Create interactive heatmap using Plotly
            fig = go.Figure(data=go.Heatmap(z=heatmap_data.values, 
                                           x=heatmap_data.columns, 
                                           y=heatmap_data.index, 
                                           colorscale='Blues', 
                                           colorbar=dict(title="Delay (minutes)"),
                                           hoverongaps=False))
            fig.update_layout(title=f'{", ".join(selected_transport)} Delays by Week ({start_year} - {end_year})', 
                              xaxis_title='Year', 
                              yaxis_title='Week')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Donut Chart for weather condition distribution
            st.write("### Donut Chart: Weather Condition Distribution")
            st.write(""" 
                This donut chart shows the distribution of different weather conditions (e.g., Fog, Rain, Snow, etc.) that caused delays.
            """)
            weather_counts = filtered_df['Weather Condition'].value_counts()
            
            # Create interactive donut chart using Plotly
            fig = go.Figure(data=[go.Pie(labels=weather_counts.index, 
                                         values=weather_counts.values, 
                                         hole=0.3, 
                                         hoverinfo='label+percent+value')])
            fig.update_layout(title=f'{", ".join(selected_transport)} Weather Condition Distribution')
            st.plotly_chart(fig, use_container_width=True)

        # Line chart for delay trends over time
        st.write("### Line Chart: Delay Trends Over Time")
        st.write(""" 
            This line chart shows how the average delay due to weather changes over time.
            By analyzing this, we can identify periods where delays were particularly severe.
        """)
        delay_over_time = filtered_df.groupby('Date')['Delay Due to Weather (minutes)'].mean().reset_index()
        
        # Create interactive line chart using Plotly
        fig = go.Figure(data=go.Scatter(x=delay_over_time['Date'], 
                                       y=delay_over_time['Delay Due to Weather (minutes)'], 
                                       mode='lines', 
                                       line=dict(color='green')))
        fig.update_layout(title=f'{", ".join(selected_transport)} Average Delay Due to Weather Over Time', 
                          xaxis_title='Date', 
                          yaxis_title='Average Delay (minutes)')
        st.plotly_chart(fig, use_container_width=True)

        # Additional Insights: Delays by Day of the Week
        st.write("### Additional Insights: Delays by Day of the Week")
        st.write(""" 
            This bar chart shows the average delay by weather condition for each day of the week.
        """)
        day_of_week_data = filtered_df.groupby([filtered_df['Date'].dt.day_name(), 'Weather Condition'])['Delay Due to Weather (minutes)'].mean().unstack()
        
        # Create interactive bar chart using Plotly
        fig = px.bar(day_of_week_data, x=day_of_week_data.index, y=day_of_week_data.columns,
                     title=f'{", ".join(selected_transport)} Average Delays by Weather Condition for Each Day of the Week')
        st.plotly_chart(fig, use_container_width=True)

        # Distribution of Delays Due to Weather
        st.write("### Distribution of Delays Due to Weather")
        st.write(""" 
            This histogram shows the distribution of delays caused by weather conditions.
        """)
        fig = px.histogram(filtered_df, x="Delay Due to Weather (minutes)", nbins=20)
        fig.update_layout(title=f'{", ".join(selected_transport)} Distribution of Delays Due to Weather')
        st.plotly_chart(fig, use_container_width=True)

        # Weather vs Delay Boxplot
        st.write("### Weather vs. Delay")
        st.write(""" 
            This boxplot shows how delays vary depending on the weather conditions.
            It helps identify whether certain weather conditions, such as snow or rain, cause higher delays on average.
        """)
        fig = px.box(filtered_df, x="Weather Condition", y="Delay Due to Weather (minutes)", 
                     title=f'{", ".join(selected_transport)} Delay Due to Weather by Weather Condition')
        st.plotly_chart(fig, use_container_width=True)

        # Conclusion Section
        st.subheader('Conclusion')
        st.write(""" 
            This dashboard provides insights into the relationship between weather conditions and public transport delays.
            By analyzing these patterns, we can improve service delivery and minimize delays during adverse weather conditions.
        """)
        
        # Feedback Section
        st.subheader('Feedback')
        st.write("Your feedback is valuable! Please provide any comments or suggestions below.")
        feedback = st.text_area("Your Feedback")
        if st.button("Submit Feedback"):
            st.write("Thank you for your feedback!")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Load the data
df = pd.read_csv('data/5_Years_Weather_Impact_on_Public_Transport.csv')  # Ensure the correct file path

# Convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Sidebar configuration
st.sidebar.header('Dashboard Controls')

# Sidebar: Select transport types (Bus, Train, etc.)
transport_types = df['Public Transport Route'].unique()
selected_transport = st.sidebar.multiselect('Select Transport Type(s)', options=transport_types, default=transport_types)

# Sidebar: Select year range (Start and End Year)
start_year = st.sidebar.selectbox('Select Start Year', options=sorted(df['Date'].dt.year.unique()), index=0)
end_year = st.sidebar.selectbox('Select End Year', options=sorted(df['Date'].dt.year.unique()), index=len(df['Date'].dt.year.unique())-1)

# Sidebar: Select weather condition
weather_conditions = df['Weather Condition'].unique()
selected_weather_conditions = st.sidebar.multiselect('Select Weather Condition(s)', options=weather_conditions, default=weather_conditions)

# Sidebar: Select time of day (Off-Peak or Rush Hour)
time_of_day = st.sidebar.multiselect('Select Time of Day', ['Off-Peak', 'Rush Hour'], default=['Off-Peak', 'Rush Hour'])

# Ensure the user has selected both year range and transport type(s)
if not selected_transport or not start_year or not end_year:
    st.markdown(""" 
        # Welcome to the Impact of Weather on Public Transport Dashboard!
        Please select both a year range and transport type(s) from the sidebar to view the data.
    """)
else:
    st.header(f"Impact of Weather on Selected Transport for {start_year} - {end_year}")
    
    # Filter data based on the selected year range, transport type(s), and weather conditions
    filtered_df = df[(df['Date'].dt.year >= start_year) & (df['Date'].dt.year <= end_year) & df['Public Transport Route'].isin(selected_transport)]
    if selected_weather_conditions:
        filtered_df = filtered_df[filtered_df['Weather Condition'].isin(selected_weather_conditions)]
    if time_of_day:
        filtered_df = filtered_df[filtered_df['Time of Day'].isin(time_of_day)]
    
    # Check if the filtered data is empty
    if filtered_df.empty:
        st.warning("No data available for the selected filters. Please adjust your selections.")
    else:
        # Display message with selected filters
        st.markdown(f"### Showing data for: {start_year} to {end_year} and {', '.join(selected_transport)}")

        # Key Performance Indicators (KPIs)
        st.subheader('Key Performance Indicators (KPIs)')
        col1, col2, col3 = st.columns(3)

        # Total Delays (minutes)
        total_delays = int(filtered_df['Delay Due to Weather (minutes)'].sum())
        col1.metric("Total Delays (minutes)", f"{total_delays:,}", delta=total_delays)

        # Total Routes Affected
        total_routes = int(filtered_df['Public Transport Route'].nunique())
        col2.metric("Total Routes Affected", total_routes)

        # Average Delay (minutes)
        avg_delay = float(filtered_df['Delay Due to Weather (minutes)'].mean())
        col3.metric("Average Delay (minutes)", f"{avg_delay:.1f}", delta=avg_delay)

        # --- Visualization Section ---
        st.subheader('Visualizations')

        # Create columns for side-by-side visualization
        col1, col2 = st.columns(2)

        with col1:
            # Interactive Heatmap for delays over time (Weekly Data)
            st.write("### Heatmap: Delays Over Time (Weekly)")
            st.write(""" 
                This heatmap shows how weather delays are distributed across weeks and years.
                The values represent the total delays due to weather conditions, categorized by week and year.
            """)
            heatmap_data = filtered_df.pivot_table(values='Delay Due to Weather (minutes)', 
                                                   index=filtered_df['Date'].dt.isocalendar().week, 
                                                   columns=filtered_df['Date'].dt.year, 
                                                   aggfunc=np.sum)
            fig = px.imshow(heatmap_data, 
                            labels=dict(x="Week", y="Year", color="Total Delays (minutes)"), 
                            title="Delays Over Time (Weekly)")
            st.plotly_chart(fig)

        with col2:
            # Interactive Donut Chart for weather condition distribution
            st.write("### Donut Chart: Weather Condition Distribution")
            st.write(""" 
                This donut chart shows the distribution of different weather conditions (e.g., Fog, Rain, Snow, etc.) that caused delays.
            """)
            weather_counts = filtered_df['Weather Condition'].value_counts()
            fig = px.pie(values=weather_counts, names=weather_counts.index, hole=0.3, title="Weather Condition Distribution")
            st.plotly_chart(fig)

        # Line chart for delay trends over time
        st.write("### Line Chart: Delay Trends Over Time")
        st.write(""" 
            This line chart shows how the average delay due to weather changes over time.
            By analyzing this, we can identify periods where delays were particularly severe.
        """)
        delay_over_time = filtered_df.groupby('Date')['Delay Due to Weather (minutes)'].mean()
        fig = px.line(delay_over_time, x=delay_over_time.index, y=delay_over_time, title="Average Delay Due to Weather Over Time")
        st.plotly_chart(fig)

        # Additional Insights: Delays by Day of the Week
        st.write("### Additional Insights: Delays by Day of the Week")
        st.write(""" 
            This bar chart shows the average delay by weather condition for each day of the week.
        """)
        day_of_week_data = filtered_df.groupby([filtered_df['Date'].dt.day_name(), 'Weather Condition'])['Delay Due to Weather (minutes)'].mean().unstack()
        fig = day_of_week_data.plot(kind='bar', stacked=True, colormap='Set2', figsize=(10,6))
        st.pyplot(fig)

        # Distribution of Delays Due to Weather
        st.write("### Distribution of Delays Due to Weather")
        st.write(""" 
            This histogram shows the distribution of delays caused by weather conditions.
        """)
        fig = px.histogram(filtered_df, x='Delay Due to Weather (minutes)', title="Distribution of Delays Due to Weather")
        st.plotly_chart(fig)

        # Weather vs Delay Boxplot
        st.write("### Weather vs. Delay")
        st.write(""" 
            This boxplot shows how delays vary depending on the weather conditions.
            It helps identify whether certain weather conditions, such as snow or rain, cause higher delays on average.
        """)
        fig = px.box(filtered_df, x="Weather Condition", y="Delay Due to Weather (minutes)", title="Delay Due to Weather by Weather Condition")
        st.plotly_chart(fig)

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

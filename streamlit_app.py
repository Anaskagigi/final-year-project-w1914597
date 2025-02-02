import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set up page configuration
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# Inject custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Sidebar for parameter selection
st.sidebar.header('Dashboard `version 2`')

# Sidebar settings for heatmap
time_hist_color = st.sidebar.selectbox('Color by', ('temp_min', 'temp_max'))

# Sidebar settings for donut chart
donut_theta = st.sidebar.selectbox('Select data', ('q2', 'q3'))

# Sidebar settings for line chart
plot_data = st.sidebar.multiselect('Select data', ['temp_min', 'temp_max'], ['temp_min', 'temp_max'])
plot_height = st.sidebar.slider('Specify plot height', 200, 500, 250)

# Footer
st.sidebar.markdown('---')
st.sidebar.markdown('Created with ❤️ by [Your Name](https://github.com)')

# Load dataset for the dashboard
df = pd.read_csv('data/5_Years_Weather_Impact_on_Public_Transport.csv')

# Filter data based on user selection
st.sidebar.subheader('Select Time Frame')
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(df['Date'].min()).date())
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(df['Date'].max()).date())

filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
filtered_df = filtered_df[filtered_df['Public Transport Route'] != 'No Service']

# Display metrics
st.markdown('### Key Performance Indicators (KPIs)')
col1, col2, col3 = st.columns(3)
col1.metric("Total Delays (minutes)", f"{filtered_df['Delay Due to Weather (minutes)'].sum():,}")
col2.metric("Total Routes Affected", filtered_df['Public Transport Route'].nunique())
col3.metric("Average Delay (minutes)", f"{filtered_df['Delay Due to Weather (minutes)'].mean():.1f}")

# Visualizations Section
st.subheader('Visualizations')

# Heatmap for delays over time
st.write("### Heatmap: Delays Over Time (Weekly)")
heatmap_data = filtered_df.pivot_table(values='Delay Due to Weather (minutes)', 
                                       index=filtered_df['Date'].dt.week, 
                                       columns=filtered_df['Date'].dt.year, 
                                       aggfunc=np.sum)
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=False, cmap='Blues', ax=ax)
ax.set_title('Weather Delays by Week (Yearly Breakdown)')
st.pyplot(fig)

# Donut Chart for weather condition distribution
st.write("### Donut Chart: Weather Condition Distribution")
weather_counts = filtered_df['Weather Condition'].value_counts()
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(weather_counts, labels=weather_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette("Set3", len(weather_counts)))
ax.axis('equal')  # Equal aspect ratio ensures that pie chart is drawn as a circle.
ax.set_title('Distribution of Weather Conditions')
st.pyplot(fig)

# Line chart for delay trends over time
st.write("### Line Chart: Delay Trends Over Time")
delay_over_time = filtered_df.groupby('Date')['Delay Due to Weather (minutes)'].mean()
fig, ax = plt.subplots(figsize=(10, 6))
delay_over_time.plot(kind='line', ax=ax, color='green')
ax.set_xlabel('Date')
ax.set_ylabel('Average Delay Due to Weather (minutes)')
ax.set_title('Average Delay Due to Weather Over Time')
st.pyplot(fig)

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

st.write("Dashboard developed by Anas Kagigi - w1914597")

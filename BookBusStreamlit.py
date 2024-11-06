import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
from datetime import time

# Connect to SQLite database
db_engine = create_engine('sqlite:///redbusDetails.db')

def run_streamlit_app():
    st.title('Redbus Data Scraping and Filtering')

    # Load data from SQL database
    bus_df = pd.read_sql_table('bus_routes', db_engine)

    # Convert price and rating to numeric, filling NaN values with default values
    bus_df['price'] = pd.to_numeric(bus_df['price'], errors='coerce').fillna(0)
    bus_df['bus_rating'] = pd.to_numeric(bus_df['bus_rating'], errors='coerce').fillna(0)
    
    if (bus_df['price'] == 0).all():        
        st.warning("All prices are showing as 0. Please check the source data for accuracy.")

    # Sidebar filters
    st.sidebar.title('Filters')
    bus_type = st.sidebar.multiselect('Bus Type', bus_df['bustype'].unique())
    bus_names = st.sidebar.multiselect('Bus Name', bus_df['busname'].unique())
    
    # Route Filter
    routes = st.sidebar.multiselect('Route', bus_df['route_name'].unique())
    
    # Departure Time Filter: Dropdown of scraped times and manual entry
    st.sidebar.markdown("### Departure Time")
    depart_times = st.sidebar.multiselect('Select from Scraped Times', bus_df['departing_time'].unique())

    # Add manual time entry
    manual_depart_time = st.sidebar.time_input('Enter Desired Time Manually', value=None)

    # State Filter
    state = st.sidebar.multiselect('State', bus_df['state_name'].unique())

    # Ensure that min and max values for sliders are not NaN
    min_price = float(bus_df['price'].min())
    max_price = float(bus_df['price'].max())
    min_rating = float(bus_df['bus_rating'].min())
    max_rating = float(bus_df['bus_rating'].max())

    # Provide default range if min and max are the same
    if min_price == max_price:
        min_price, max_price = 0, 3000
    if min_rating == max_rating:
        min_rating, max_rating = 0, 5

    price_range = st.sidebar.slider('Price Range', min_price, max_price, (min_price, max_price))
    rating = st.sidebar.slider('Rating', min_rating, max_rating, (min_rating, max_rating))

    availability = st.sidebar.multiselect('Availability', bus_df['seats_available'].unique())

    # Filter data based on user inputs
    filtered_df = bus_df
    if bus_type:
        filtered_df = filtered_df[filtered_df['bustype'].isin(bus_type)]
    if bus_names:
        filtered_df = filtered_df[filtered_df['busname'].isin(bus_names)]
    if routes:
        filtered_df = filtered_df[filtered_df['route_name'].isin(routes)]
    
    # Filter by either the selected scraped time or manually entered time
    if depart_times:
        filtered_df = filtered_df[filtered_df['departing_time'].isin(depart_times)]
    elif manual_depart_time is not None:
        # Convert scraped departing_time column to datetime.time for comparison
        bus_df['departing_time'] = pd.to_datetime(bus_df['departing_time'], format='%H:%M', errors='coerce').dt.time
        filtered_df = filtered_df[filtered_df['departing_time'] == manual_depart_time]

        # Display message if no buses are available for the selected manual time
        if filtered_df.empty:
            st.warning(f"No buses available for the selected time: {manual_depart_time}")

    # State Filter
    if state:
        filtered_df = filtered_df[filtered_df['state_name'].isin(state)]

    # Price and rating range filtering
    filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]
    filtered_df = filtered_df[(filtered_df['bus_rating'] >= rating[0]) & (filtered_df['bus_rating'] <= rating[1])]
    if availability:
        filtered_df = filtered_df[filtered_df['seats_available'].isin(availability)]

    # Remove NaN values and sort the data
    filtered_df = filtered_df.dropna(subset=['price', 'bus_rating'])
    filtered_df = filtered_df.sort_values(by=['price'])

    # Display filtered data
    st.subheader('Bus Search Results')
    st.dataframe(filtered_df)

if __name__ == "__main__":
    run_streamlit_app()

import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

# Connect to SQLite database
db_engine = create_engine('sqlite:///redbusDetails.db')

def run_streamlit_app():
    st.title('Redbus Data Scraping and Filtering')

    # Load data from SQL database
    bus_df = pd.read_sql_table('bus_routes', db_engine)

    # Convert price and rating to numeric, filling NaN values with default values
    bus_df['price'] = pd.to_numeric(bus_df['price'], errors='coerce').fillna(0)
    bus_df['bus_rating'] = pd.to_numeric(bus_df['bus_rating'], errors='coerce').fillna(0)

    # Sidebar filters
    st.sidebar.title('Filters')
    bus_type = st.sidebar.multiselect('Bus Type', bus_df['bustype'].unique())
    
    # Ensure that min and max values for sliders are not NaN
    min_price = float(bus_df['price'].min())
    max_price = float(bus_df['price'].max())
    min_rating = float(bus_df['bus_rating'].min())
    max_rating = float(bus_df['bus_rating'].max())

    # Provide default range if min and max are NaN or equal
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



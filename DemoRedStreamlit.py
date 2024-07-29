import streamlit as st
import pandas as pd

# Function to load data
@st.cache_data
def load_data():
    # Load the CSV file into a DataFrame
    df = pd.read_csv('redbusData.csv')
    return df

# Main function to display the Streamlit app
def main():
    st.title('Redbus Data Scraper')
    st.write('This application displays bus data scraped from Redbus.')

    # Load data
    data = load_data()

    # Display the DataFrame in Streamlit
    st.dataframe(data)

    # Add filters for user interaction
    bus_type_filter = st.selectbox('Select Bus Type', options=['All'] + list(data['bus_type'].unique()))
    bus_name_filter = st.selectbox('Select Bus Name', options=['All'] + list(data['bus_name'].unique()))

    filtered_data = data.copy()
    if bus_type_filter != 'All':
        filtered_data = filtered_data[filtered_data['bus_type'] == bus_type_filter]

    if bus_name_filter != 'All':
        filtered_data = filtered_data[filtered_data['bus_name'] == bus_name_filter]

    st.write('Filtered Data:')
    st.dataframe(filtered_data)

if __name__ == "__main__":
    main()

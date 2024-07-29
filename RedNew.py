import os
import time
import pandas as pd
from sqlalchemy import create_engine, text
from selenium import webdriver
#from selenium.webdriver.chrome import Service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymysql as mysql
import streamlit as st

# Specify the path to ChromeDriver
chrome_driver_path = "C:/Users/Lenovo/.cache/selenium/chromedriver/win64/126.0.6478.126/chromedriver.exe"

# Set up Selenium driver with the specified path
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Connect to SQL database
db_engine = create_engine('sqlite:///redbusDetails.db')
#db_engine = create_engine('mysql+pymysql://root:Jsd@1908@localhost/redbus')
def create_database_and_table():
    with db_engine.connect() as con:
        con.execute(text("""
        CREATE TABLE IF NOT EXISTS bus_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route_name TEXT,
            route_link TEXT,
            busname TEXT,
            bustype TEXT,
            departing_time TEXT,
            duration TEXT,
            reaching_time TEXT,
            star_rating REAL,
            price REAL,
            seats_available INTEGER
        )
        """))

def insert_data_from_csv():
    csv_file_path = 'redbusDetails.csv'
    bus_df = pd.read_csv(csv_file_path)
    print(bus_df.columns)
    with db_engine.connect() as con:
        bus_df.to_sql('bus_routes', con, if_exists='replace', index=False)

    for index, row in bus_df.iterrows():
        # Clean the price string
        price_str = row['price'].replace('₹', '').replace('INR', '').replace(',', '').strip()
        
        # If the price string contains "Starts from", handle it accordingly
        if 'Starts from' in price_str:
            price_str = price_str.split('\n')[1].strip()  # Get the actual price

        # Convert cleaned price string to float
        try:
            price_value = float(price_str)
        except ValueError:
            print(f"Could not convert price '{price_str}' to float.")
            price_value = None  # Handle the case where conversion fails

        

# Scrape Redbus data
def scrape_redbusData():
    # Navigate to Redbus homepage
    driver.get('https://www.redbus.in/bus-tickets/neyveli-to-coimbatore?fromCityName=Neyveli&fromCityId=68815&srcCountry=IND&toCityName=Coimbatore&toCityId=141&destCountry=IND&onward=10-Aug-2024&opId=0&busType=Any')
    driver.maximize_window()
    
    # Wait for search results to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "clearfix bus-item")]')))

    # Scroll down to load more bus items
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new bus items to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Scrape bus data
    bus_details = []    
    bus_items = driver.find_elements(By.XPATH, '//div[contains(@class, "clearfix bus-item")]')  # Selector for bus items
    for bus_item in bus_items:
        
        bus_name = bus_item.find_element(By.XPATH, './/div[contains(@class, "travels")]').text  # Selector for bus name
        bus_type = bus_item.find_element(By.XPATH, './/div[contains(@class, "bus-type")]').text  # Selector for bus type
        bus_price = bus_item.find_element(By.XPATH, './/div[contains(@class, "fare")]').text  # Selector for bus fare
        bus_rating = bus_item.find_element(By.XPATH, './/div[contains(@class, "rating")]').text  # Selector for bus rating
        bus_availability = bus_item.find_element(By.XPATH, './/div[contains(@class, "seat-left")]').text  # Selector for availability
        dept_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "dp-time")]').text  # Selector for departure time
        arr_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "bp-time")]').text  # Selector for arrival time
        dur_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "dur")]').text  # Selector for duration

        print(f"Bus Type: {bus_type}, Bus Name: {bus_name}, Bus Price: {bus_price}, Bus Rating: {bus_rating}, Bus Availability: {bus_availability}, Departure: {dept_time}, Arrival: {arr_time}, Duration: {dur_time}")
        print("*********************************")
        bus_details.append({
            'route_name': 'Neyveli to coimbatore',  # Example route name
            'route_link': driver.current_url,
            'bustype': bus_type,
            'busname': bus_name,
            'price': bus_price.replace('₹', '').replace(',', '').strip(),  
            'bus_rating': bus_rating.strip(),
            'seats_available': bus_availability.strip(),
            'departing_time': dept_time.strip(),
            'reaching_time': arr_time.strip(),
            'duration': dur_time.strip()
        })

    # Store scraped data in CSV
    bus_df = pd.DataFrame(bus_details)
    bus_df=bus_df.drop_duplicates()
    
    csv_file_path = 'redbusDetails.csv'
    bus_df.to_csv(csv_file_path, index=False, mode='w', header=True)  # Overwrite the CSV file
    print(f"Data saved to {csv_file_path}")

    # Insert data into MySQL database
    insert_data_from_csv()

if __name__ == "__main__":
    create_database_and_table()  # Create database and table
    scrape_redbusData()  # Scrape Redbus data
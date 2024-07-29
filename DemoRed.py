import os
import time
import pandas as pd
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import streamlit as st
#Working without sql con

# Set up Selenium driver
#driver = webdriver.Chrome()

# Connect to SQL database
#db_engine = create_engine('sqlite:///redbus_data.db')

# Specify the path to ChromeDriver
chrome_driver_path = r"C:\Users\Lenovo\.cache\selenium\chromedriver\win64\126.0.6478.126\chromedriver.exe"

# Set up Selenium driver with the specified path
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)


# Connect to SQL database
db_engine = create_engine('sqlite:///redbus_data.db')




# Scrape Redbus data
def scrape_redbus_data():
    # Navigate to Redbus homepage
    driver.get('https://www.redbus.in/bus-tickets/neyveli-to-coimbatore?fromCityName=Neyveli&fromCityId=68815&srcCountry=IND&toCityName=Coimbatore&toCityId=141&destCountry=IND&onward=01-Aug-2024&opId=0&busType=Any')
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
    bus_data = []
    
    scraped_bus_names = set()  # Set to track unique bus names
    
    bus_items = driver.find_elements(By.XPATH, '//div[contains(@class, "clearfix bus-item")]')  # Selector for bus items
    for bus_item in bus_items:
        
        bus_name = bus_item.find_element(By.XPATH, './/div[contains(@class, "travels")]').text  # Selector for bus name
        if bus_name in scraped_bus_names:
            continue  # Skip this bus if it has already been scraped

        
        
        bus_type = bus_item.find_element(By.XPATH, './/div[contains(@class, "bus-type")]').text  # Selector for bus type
        bus_name = bus_item.find_element(By.XPATH, './/div[contains(@class, "travels")]').text  # Selector for bus name
        bus_price = bus_item.find_element(By.XPATH, './/div[contains(@class, "fare")]').text  # Selector for bus fare
        bus_rating = bus_item.find_element(By.XPATH, './/div[contains(@class, "rating")]').text  # Selector for bus rating
        bus_availability = bus_item.find_element(By.XPATH, './/div[contains(@class, "seat-left")]').text  # Selector for availability
        dept_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "dp-time")]').text  # Selector for bus type
        arr_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "bp-time")]').text  # Selector for bus type
        dur_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "dur")]').text  # Selector for bus type

        
        print(f"Bus Type: {bus_type}, Bus Name: {bus_name}, Bus Price: {bus_price}, Bus Rating: {bus_rating},bus_availability:{bus_availability},Departure: {dept_time},Arival:{arr_time},Duration: {dur_time}")
        print("-----------------------------------------------------------------")
        
        bus_data.append({
            'route_name': 'Neyveli to Coimbatore',  # Example route name
            'route_link': driver.current_url,
            'bus_type': bus_type,
            'bus_name': bus_name,
            'bus_price': bus_price.replace('₹', '').replace(',', '').strip(),  # Clean price
            'bus_rating': bus_rating.strip(),
            'bus_availability': bus_availability.strip(),
            'dept_time':dept_time.strip(),
            'arr_time':arr_time.strip(),
            'dur_time':dur_time.strip()
        })

        # Store scraped data in CSV - new piece
    bus_df = pd.DataFrame(bus_data)
    bus_df=bus_df.drop_duplicates()
    
    csv_file_path = 'redbusData.csv'
    bus_df.to_csv(csv_file_path, index=False, mode='w', header=True)  # Overwrite the CSV file
    print(f"Data saved to {csv_file_path}")
#new piece

    # Store scraped data in SQL database
    bus_df = pd.DataFrame(bus_data)
    bus_df=bus_df.drop_duplicates()
    #bus_df.to_sql('bus_data', db_engine, if_exists='replace', index=False)
    bus_df.to_csv(csv_file_path, index=False, mode='w', header=True)  # Overwrite the CSV file
    print("**************************")
    print(bus_df)
if __name__ == "__main__":
    # Scrape Redbus data
    scrape_redbus_data()

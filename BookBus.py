import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from sqlalchemy import create_engine, text
#from selenium.webdriver.chrome import Service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pymysql as mysql
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

# Initialize the ChromeDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)  # Increased timeout

# List to store RTC names and links (First Script Part)
rtc_data = []

#Scrape RTC names and links from the South region
driver.get("https://www.redbus.in/online-booking/rtc-directory")
driver.maximize_window()

# Define a function to scrape the RTC links from the South region
def scrape_rtc_links():
    try:
        south_section = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#root > div > article:nth-child(4) > div > div > ul:nth-child(2)')))
        rtc_list_items = south_section.find_elements(By.CSS_SELECTOR, 'li.D113_item_rtc')

        for li in rtc_list_items:
            try:
                # Extract the <a> tag from each <li>
                a_tag = li.find_element(By.TAG_NAME, 'a')
                # Extract the RTC name and link
                rtc_name = a_tag.text
                rtc_link = a_tag.get_attribute('href')
                # Append to rtc_data list
                rtc_data.append({'name': rtc_name, 'link': rtc_link})
            except Exception as e:
                print(f"An error occurred while processing an RTC item: {e}")
    except Exception as e:
        print(f"An error occurred while locating the South section: {e}")

# Scrape the RTC links from the South region
scrape_rtc_links()

# Print scraped RTC data (optional)
print("\nScraped RTC Names and Links from the South Region:\n")
for entry in rtc_data:
    print(f"RTC Name: {entry['name']} | Link: {entry['link']}")

# Store the South region bus data in a dataframe and CSV
#South_Region = pd.DataFrame(rtc_data, columns=['Operator Name', 'Operator Link'])
#South_Region.to_csv('South_Region_details.csv', index=False)
South_Region = pd.DataFrame(rtc_data)
South_Region.to_csv('South_Region_details.csv', index=False)

    
# Define a list to store all route data (Second Script Part)
all_route_data = []

#Scrape route data for each RTC link from rtc_data
def scrape_route_data(link,name):
    try:
        driver.get(link)
        time.sleep(3)  # Wait for the page to load
        
        def scrape_page():
            try:
                # Locate the route container and get route details
                routescontainer = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.route")))
                for route in routescontainer:
                    try:
                        routename = route.text  # Extracts the route name
                        routelink = route.get_attribute('href')  # Extracts the href link
                        all_route_data.append({'state': name,'routename': routename, 'routelink': routelink})
                    except Exception as e:
                        print(f"Error extracting route data: {e}")
            except Exception as e:
                #print(f"Error locating route container: {e}")
                print("No data to extract")

        # Scrape the first 5 pages (or all available pages)
        for page_number in range(1, 6):
            scrape_page()
            if page_number < 5:
                try:
                    # Locate the pagination container and navigate to the next page
                    pagination_container = wait.until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="root"]/div/div[4]/div[12]')))  # change
                    next_page_button = pagination_container.find_element(
                        By.XPATH, f'.//div[contains(@class, "DC_117_pageTabs") and text()="{page_number + 1}"]')

                    actions = ActionChains(driver)
                    actions.move_to_element(next_page_button).perform()
                    time.sleep(1)  # Wait after scrolling

                    # Click the next page button
                    next_page_button.click()

                    # Wait until the next page is active
                    wait.until(EC.text_to_be_present_in_element(
                        (By.XPATH, '//div[contains(@class, "DC_117_pageTabs DC_117_pageActive")]'), str(page_number + 1)))

                    time.sleep(3)  # Wait for the next page to load fully
                except Exception as e:
                    #print(f"Error navigating to page {page_number + 1}: {e}")
                    print("No more pages to navigate.")
                    break

    except Exception as e:
        print(f"Error navigating to RTC link {link}: {e}")

# Loop through each RTC link in rtc_data and scrape route data
for rtc in rtc_data:
    print(f"\nScraping route data for {rtc['name']} from {rtc['link']}\n")
    scrape_route_data(rtc['link'],rtc['name'])

# Print the scraped route data
print("\nAll Scraped Route Data:\n")

# Store the bus data in a dataframe and CSV
#SR_details = pd.DataFrame(all_route_data, columns=['Route Name', 'Route Link'])
#SR_details.to_csv('SR_Bus_details.csv', index=False)
SR_details = pd.DataFrame(all_route_data)
SR_details.to_csv('SR_Bus_details.csv', index=False)
for entry in all_route_data:
    print(entry)

# Close the driver after scraping
driver.quit()



# Specify the path to ChromeDriver
chrome_driver_path = r"C:\Users\Lenovo\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Set up Selenium driver with the specified path
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Connect to SQL database
db_engine = create_engine('sqlite:///redbusDetails.db')
#db_engine = create_engine('mysql+pymysql://root:Jsd@1908@localhost/redbusDetails')


    
    
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
            seats_available INTEGER,
            state_name TEXT
               
        )
        """))

# Function to extract price from the price string
def extract_price(price_str):
    price_str = price_str.replace('₹', '').replace('INR', '').replace(',', '').strip()

    # If price contains multiple values like "INR 1999 1924"
    if ' ' in price_str:
        price_str = price_str.split(' ')[-1]  # Take the last value as the price

    # Handle "Starts from" case
    if 'Starts from' in price_str:
        price_str = price_str.split('\n')[-1].strip()

    try:
        price_value = float(price_str)
    except ValueError:
        price_value = None  # Handle the case where conversion fails

    return price_value

# Insert data from CSV into the SQL database
def insert_data_from_csv(csv_file_path):
    bus_df = pd.read_csv(csv_file_path)

    # Clean the price column in the dataframe
    bus_df['price'] = bus_df['price'].apply(lambda x: extract_price(str(x)))

    with db_engine.connect() as con:
        bus_df.to_sql('bus_routes', con, if_exists='replace', index=False)
        


    # Scrape Redbus data
def scrape_redbusData(new_link,new_name):
    # Navigate to Redbus homepage
    #driver.get('https://www.redbus.in/bus-tickets/neyveli-township-to-bangalore?fromCityId=215618&toCityId=122&fromCityName=Neyveli%20Township&toCityName=Bangalore&busType=Any&onward=26-Sep-2024&srcCountry=IND&destCountry=IND')
    driver.get(new_link)
    driver.maximize_window()

    bus_route_name = driver.find_element(By.XPATH, './/div[contains(@class, "D136_heading")]').text # Selector for bus route name
    
    # Wait for search results to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "clearfix bus-item")]')))

    # Scroll down to load more bus items
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  
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
        
        
        
        #bus_rating = bus_item.find_element(By.XPATH, './/div[contains(@class, "rating")]').text  # Selector for bus rating
        
        try:
            bus_rating = bus_item.find_element(By.XPATH, './/div[contains(@class, "rating")]').text
            #print(f"Bus Rating: {bus_rating}")
        except NoSuchElementException:
            print("No Rating")

        bus_availability = bus_item.find_element(By.XPATH, './/div[contains(@class, "seat-left")]').text  # Selector for availability
        dept_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "dp-time")]').text  # Selector for departure time
        arr_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "bp-time")]').text  # Selector for arrival time
        dur_time = bus_item.find_element(By.XPATH, './/div[contains(@class, "dur")]').text  # Selector for duration

        print(f"Bus Route: {bus_route_name},Bus Type: {bus_type}, Bus Name: {bus_name}, Bus Price: {bus_price}, Bus Rating: {bus_rating}, Bus Availability: {bus_availability}, Departure: {dept_time}, Arrival: {arr_time}, Duration: {dur_time}")
        print("*********************************")
        bus_details.append({
            'route_name':bus_route_name,  # Example route name
            'route_link': driver.current_url,
            'bustype': bus_type,
            'busname': bus_name,
            'price': bus_price.replace('₹', '').replace(',', '').strip(),  
            'bus_rating': bus_rating.strip(),
            'seats_available': bus_availability.strip(),
            'departing_time': dept_time.strip(),
            'reaching_time': arr_time.strip(),
            'duration': dur_time.strip(),
            'state_name':new_name
            
        })

    # Store scraped data in CSV
    bus_df = pd.DataFrame(bus_details)
    bus_df=bus_df.drop_duplicates()

    # Clean the price column before saving to CSV
    bus_df['price'] = bus_df['price'].apply(lambda x: extract_price(str(x)))
    print(bus_df.price)

    csv_file_path = 'redbusDetails.csv'
    bus_df.to_csv(csv_file_path, index=False, mode='w', header=True)  # Overwrite the CSV file
    print(f"Data saved to {csv_file_path}")

    # Insert data into MySQL database
    insert_data_from_csv(csv_file_path)
    
        

if __name__ == "__main__":
    create_database_and_table()  # Create database and table
    j=0
    while j<1:
        scrap_link=all_route_data[j]['routelink']
        state_name=all_route_data[j]['state']
        scrape_redbusData(scrap_link,state_name)  # Scrape Redbus data
        j=j+1


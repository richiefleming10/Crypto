"""
_________________________________________________________________________________________________________
Main Methods for conducting automated technical analysis on Coinbase top 100 coins based on market cap.
    - Developed by: Richard A. Fleming 2024
"""

import pandas as pd
import numpy as np 
import os 
import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import datetime
from Utility.Stats.technical_indicators import stochastic_oscillator

def daily_stochatsic(directory, stochastic_days):
    stochastic_tensor = np.full((29, 200), 0.0, dtype=np.float64) #2 rows for fast k, slow k : 100 cols for 100 different coins 
    sto_counter = 0
    delimiter_one = "-"
    delimiter_two = "_"
    headers = []
    folder_path = "daily_analysis_data"
    for filename in os.listdir(directory):
        if filename.endswith('csv'):
            coin_name = (filename.split(delimiter_one, 1)[0] 
                         if len(filename.split(delimiter_one, 1)[0]) < len(filename.split(delimiter_two, 1)[0]) 
                         else filename.split(delimiter_two, 1)[0])
            headers.append(f"{coin_name}-Fast-K")
            headers.append(f"{coin_name}-Slow-K")
            file_path = os.path.join(directory, filename)
            data = pd.read_csv(file_path)
            data_np = data.iloc[1:, 2: ].to_numpy() #remove the dates row and convert to NP, remove headers 
            (fast_k, slow_k) = stochastic_oscillator(data_np, stochastic_days)
            stochastic_tensor[:, sto_counter] = fast_k
            stochastic_tensor[:, sto_counter + 1] = slow_k
            sto_counter += 2
            print(f"Stochastic {filename} added to tensor")
    current_time = datetime.datetime.now()
    output_file = os.path.join(folder_path, f'daily_stochastic{current_time.hour}-{current_time.month}--{current_time.day}.xlsx')
    stochatic_df = pd.DataFrame(stochastic_tensor)
    # stochatic_df.columns = headers
    stochatic_df.to_excel(output_file, index=False)
    print('Processed Daily Stochastic')


def get_coin_links():
    # Initialize Selenium WebDriver with headless options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Remove this option if you want to see the browser actions
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Open the webpage
    url = "https://coincodex.com/"
    driver.get(url)
    
    # Initialize variables
    coin_links = []
    collected_coins = set()  # To avoid duplicates
    scroll_pause_time = 1.5  # Adjust based on your internet speed and page load time
    scroll_increment = 500  # Pixels to scroll each time
    max_scroll_attempts = 100  # Safety measure to prevent infinite loops
    
    # Get the initial scroll height
    new_scroll_position = 0
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        # Scroll down by the increment
        new_scroll_position += scroll_increment
        driver.execute_script(f"window.scrollTo(0, {new_scroll_position});")
        time.sleep(scroll_pause_time)
        
        # Find all visible coin elements
        coin_elements = driver.find_elements(By.CSS_SELECTOR, 'table tr td a[href*="/crypto/"]')
        
        # Collect coin names and URLs
        for elem in coin_elements:
            coin_name = elem.text.strip()
            href = elem.get_attribute('href')
            if coin_name and href and coin_name not in collected_coins:
                coin_url = f"{href}historical-data/"
                coin_links.append((coin_name, coin_url))
                collected_coins.add(coin_name)
                print(f"Collected: {coin_name}")
        
        # Check if we've reached the bottom of the page
        # You can implement logic to detect if new content is loaded
        if new_scroll_position >= driver.execute_script("return document.body.scrollHeight"):
            # Try to click on "Load More" button if it exists
            try:
                load_more_button = driver.find_element(By.CSS_SELECTOR, 'a.js-load-more-btn')
                if load_more_button.is_displayed():
                    load_more_button.click()
                    time.sleep(scroll_pause_time)
                else:
                    break  # No more content to load
            except:
                break  # No "Load More" button, exit the loop
        
        # Update scroll attempt counter
        scroll_attempts += 1
    
    # Close the Selenium WebDriver
    driver.quit()
    
    return coin_links

def download_data(coin_links, directory):
    chrome_options = Options()
    prefs = {"download.default_directory":directory}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Set up the WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for coin_name, coin_url in coin_links:
        try:
            print(f"Processing {coin_name}...")
            driver.get(coin_url)
            # time.sleep()  # Allow time for the page to load

            # Find and click the export button
            export_button = driver.find_element(By.XPATH, "/html/body/app-root/app-root/div/div/div/div[1]/app-coin-history-data/section[1]/div/div[3]/div[4]")
            export_button.click()
            time.sleep(3)  # Allow time for the file to download
        except Exception as e:
            print(f"Failed to process {coin_name}: {e}")

    # Close the WebDriver
    driver.quit()


def remove_directory_files(dir_path):
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Deleted {filename}")

if __name__ == "__main__":
    counter = 0
    while True: #Run once or twice a day, a few hours before you want the code to execute
        current_time = datetime.datetime.now()
        if (current_time.hour == 8 or current_time.hour == 12 or current_time.hour == 18) and counter == 0:
            download_directory = os.path.join(os.getcwd(), "coin_historical_data")
            if not os.path.exists(download_directory):
                os.makedirs(download_directory)
            
            counter = 1 #making this algorithm trigger at most once per hour
            # Get the list of coin links
            coin_links = get_coin_links()

            # Download historical data for each coin
            download_data(coin_links, download_directory)
            print(f"Data download complete at {current_time}")
            daily_stochatsic("coin_historical_data", 10)
            current_time = datetime.datetime.now()
            print(f"Stochastic complete at {current_time}")
            remove_directory_files("coin_historical_data")
            current_time = datetime.datetime.now()
            print(f"Files Removed and Process Finished at {current_time}")
        else:
            time.sleep(1800)
            counter = 0
 
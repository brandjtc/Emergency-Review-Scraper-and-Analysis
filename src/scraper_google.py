import pandas as pd
import re
import os
from google_play_scraper import app, Sort, reviews
from pprint import pprint
import pymongo
from pymongo import MongoClient
import datetime as dt
from tzlocal import get_localzone
import random
import time
import openpyxl
import http.client
from google_play_scraper.exceptions import NotFoundError, ExtraHTTPError
from multiprocessing import Pool
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# Read app data from Excel
app_df = pd.read_excel(r"C:\Users\antho\OneDrive\OneDrive\EmergencyComApps\data\EmergencyComData.xlsx", sheet_name='dataset')
app_links = app_df['Link to Google Play Store'].tolist()
app_names = list(app_df['App-Name'])

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_KEY"))
app_proj_db = client[os.getenv("DATABASE")]
review_collection = app_proj_db[os.getenv("COLLECTION")]
app_info_collection = app_proj_db[os.getenv("APPINFORMATION")]

# Constants
COUNT_PER_BATCH = 400  # Number of reviews to fetch per batch
SLEEP_TIME_RANGE = (1, 5)  # Range of sleep time between batches
NUM_OF_PROCESSES = 16

# Function to scrape reviews for an app
def scrape_reviews(app_info):
    app_name, app_link = app_info
    print(f"Processing app: {app_name}")
    
    # Check for invalid app link
    if pd.isnull(app_link) or not isinstance(app_link, str):
        print(f"Invalid app link: {app_link}. Skipping...")
        return

    # Extract app ID from the Google Play Store URL
    match = re.search(r"id=([^\&]+)", app_link)
    if match:
        app_id = match.group(1)
    else:
        print(f"Unable to extract app ID from URL: {app_link}. Skipping...")
        return

    try:
        # Fetch app information using the app ID
        app_info = app(app_id)
    except (NotFoundError, ExtraHTTPError):
        print(f"App {app_name} not found or error retrieving app. Skipping...")
        return
    
    start = dt.datetime.now(tz=get_localzone())
    fmt = "%m/%d/%y - %T %p"    
    
    print('-' * 40)
    print(f'***** {app_name} ***** started at {start.strftime(fmt)}\n')
    pprint(app_info)
    print()

    app_description = app_info.get('description')
    print(f"App Description: {app_description}")

    # Insert app_info into app_info_collection
    app_info_collection.insert_one(app_info)
    print()
    
    app_reviews = []
    batch_num = 0
    
    try:
        while True:
            # Fetch reviews for the app with error handling and retry logic
            try:
                rvws, token = reviews(
                    app_id,
                    lang='en',
                    country='us',
                    sort=Sort.NEWEST,
                    count=COUNT_PER_BATCH if batch_num == 0 else COUNT_PER_BATCH + 1,  # Include extra review in the first batch
                    continuation_token=token if batch_num > 0 else None
                )
            except http.client.IncompleteRead:
                print(f"IncompleteRead error occurred. Retrying request for app {app_name}...")
                continue
            
            if not rvws:
                break
                
            for r in rvws:
                # Adds app name and ID to each review
                r['app_name'] = app_name
                r['app_id'] = app_id
                r['platform'] = 'Google Play Store'
                
            app_reviews.extend(rvws)
            batch_num += 1
            
            if batch_num % 100 == 0:
                # Insert reviews into review_collection every 100 batches
                print(f'Batch {batch_num} completed.')
                if app_reviews:
                    review_collection.insert_many(app_reviews)
                    store_time = dt.datetime.now(tz=get_localzone())
                    print(f"Successfully inserted {len(app_reviews)} {app_name} reviews into collection at {store_time.strftime(fmt)}.\n")
                else:
                    print(f"No reviews found for {app_name}. Skipping insertion.\n")
                app_reviews = []
            
            time.sleep(random.randint(*SLEEP_TIME_RANGE))    
    except (NotFoundError, ExtraHTTPError):
        print(f"Error retrieving reviews for app {app_name}. Skipping...")
    
    end = dt.datetime.now(tz=get_localzone())
    print(f'\nDone scraping {app_name}.')
    print(f'Scraped a total of {len(app_reviews)} unique reviews.\n')
    
    if app_reviews:
        # Insert remaining reviews into review_collection
        review_collection.insert_many(app_reviews)
        print(f"Successfully inserted all {app_name} reviews into collection at {end.strftime(fmt)}.\n")
        print(f"Time elapsed for {app_name}: {end - start}")
    else:
        print(f"No reviews found for {app_name}. Skipping insertion.\n")
    
    print('-' * 40)
    print('\n')

if __name__ == '__main__':

    # Makes a pool of all available processes
    pool = Pool(NUM_OF_PROCESSES)

    # Create a list of tuples containing app information
    app_info_list = list(zip(app_names, app_links))

    # Apply the scrape_reviews function to each app_info tuple in the list
    results = pool.map(scrape_reviews, app_info_list)


    pool.close()
    pool.join()
    client.close()
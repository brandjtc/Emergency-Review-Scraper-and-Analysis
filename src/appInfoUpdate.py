import pandas as pd
import re
from google_play_scraper import app, Sort, reviews
from pprint import pprint
import pymongo
from pymongo import MongoClient
import datetime as dt
from tzlocal import get_localzone
import random
import time
from google_play_scraper.exceptions import NotFoundError, ExtraHTTPError


# Read app data from Excel
app_df = pd.read_excel(r'C:\Users\brand\OneDrive\EmergencyComApps\data\EmergencyComData.xlsx', sheet_name='dataset')
app_links = app_df['Link to Google Play Store'].tolist()
app_names = list(app_df['App-Name'])

# Connect to MongoDB
client = MongoClient("mongodb+srv://Nym:0Mk0q4XEtGCxTdkr@appstorescraper.ssekhzr.mongodb.net/")
app_proj_db = client['EmergencyReviewDB']
review_collection = app_proj_db['GooglePlayReviewCollection']
app_info_collection = app_proj_db['AppInfo']


# Function to scrape reviews for an app
def scrape_reviews(app_name, app_link):
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
    except (NotFoundError):
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

    # Add 'platform' key-value pair
    app_info['platform'] = 'Google Play Store'

    # Insert app_info into app_info_collection
    app_info_collection.insert_one(app_info)

app_info_collection.delete_many({"platform":{"$ne":"Apple App Store"}})

app_info_list = list(zip(app_names, app_links))
for i in range(0,len(app_names)):
    scrape_reviews(app_names[i],app_links[i])
print("done")
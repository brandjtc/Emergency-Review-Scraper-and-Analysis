import matplotlib.pyplot as plt
import os
import json
import pandas as pd
from pymongo import MongoClient 
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#Establishes connection to mongo DB
mongoDBkey=os.getenv("MONGO_KEY")
client = MongoClient(mongoDBkey)

#Selects EmergencyReviewDB as the database in Mongo to populate
mongoDBdatabase=os.getenv("DATABASE")
ios_proj_db=client[mongoDBdatabase]

#Connects to desired collection in aforementioned DB
review_collection = ios_proj_db["Sorted Reviews"]
review_collection.drop()
json_list = []
folder_path="./Generated Files/Reviews/"
# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        
        # Read the JSON file and add its content to the list
        with open(file_path) as file:
            data = json.load(file)
            json_list.append(data)
print("Inserting generated reviews into database")
review_collection.insert_many(json_list)
client.close()
print("Finished")
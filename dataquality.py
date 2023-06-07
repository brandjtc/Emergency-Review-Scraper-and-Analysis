from pymongo import MongoClient
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


#Establishes connection to mongo DB
client = MongoClient(os.getenv("MONGO_KEY"))

#Selects EmergencyReviewDB as the database in Mongo to populate
ios_proj_db=client[os.getenv("DATABASE")]

#Connects to desired collection in aforementioned DB
review_collection = ios_proj_db[os.getenv("COLLECTION")]
data= review_collection.find({},{"_id":1,"content":1,"app_name":1})

#Creates list of all reviews and gathers MongoDB document ID, the content string, and name of the app
#for later user
revList=list()
lenList=list()
idList=list()
nameList=list()


for item in data:
    if 'content' in item:
        try:
            lenList.append(len(item["content"]))
            revList.append(item["content"])
            idList.append(item['_id'])
            nameList.append(item['app_name'])
        except TypeError:
                pass
#Grabs the index of the top 100 longest reviews.
index=np.argsort(revList)[::-1][:100]
client.close()

dictList=list()

#Populates list of dictionaries to later be put in PD dataframe
for i in index:
    dictList.append({"App Name":nameList[index[i]],"Review":revList[index[i]],"Revew Length\n in Characters":lenList[index[i]],"Mongo ID":idList[index[i]]})
     
#Inserts list of dicts into a pandas dataframe
dfDictList=pd.DataFrame(dictList)

dfDictList.to_csv("./Generated Files/Top 100 Longest Reviews.csv")
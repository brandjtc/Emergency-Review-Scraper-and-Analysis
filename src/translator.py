import os
from pymongo import MongoClient
from googletrans import Translator
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

translation=Translator()

# Establishes connection to mongo DB
client = MongoClient(os.getenv("MONGO_KEY"))
app_proj_db=client[os.getenv("DATABASE")]
review_collection = app_proj_db[os.getenv("COLLECTION")]

#Translates string to English
def translateToEng(string):
    returnVal=translation.translate(string,dest='en')
    return returnVal.text

def langDetectorIOS(tempAppList):
    i=0
    try:
        j=tempAppList[i]==1
    except IndexError:
        return "Break"

    while tempAppList[i]==None:
        i+=1
    return translation.detect(tempAppList[i]["review"]).lang

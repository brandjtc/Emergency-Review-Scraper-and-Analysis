from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#Establishes connection to mongo DB
def MongoDBsetup(mongoDBcollection):
	mongoDBkey=os.getenv("MONGO_KEY")
	client = MongoClient(mongoDBkey)

	#Selects EmergencyReviewDB as the database in Mongo to populate
	mongoDBdatabase=os.getenv("DATABASE")
	proj_db=client[mongoDBdatabase]

	#Connects to desired collection in aforementioned DB
	review_collection = proj_db[mongoDBcollection]

	return review_collection
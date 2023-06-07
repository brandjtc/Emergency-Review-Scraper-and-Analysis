import openai
from scraper_ios import reqListGenerator
import pandas as pd
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#Sets openAI api key
openai.api_key = os.environ.get("OPEN_AI_KEY")

#Establishes connection to mongo DB
client = MongoClient("mongodb+srv://Nym:0Mk0q4XEtGCxTdkr@appstorescraper.ssekhzr.mongodb.net/")

#Selects EmergencyReviewDB as the database in Mongo to populate
ios_proj_db=client['EmergencyReviewDB']

#Connects to tables in aforementioned DB
ios_review_collection=ios_proj_db['GooglePlayReviewCollection']


#Reads excel doc using Pandas library
ios_excel=pd.read_excel(r'C:\Users\brand\OneDrive\EmergencyComApps\data\EmergencyComData.xlsx',usecols='A,L')
definitionJSON=pd.read_json(r'C:\Users\brand\OneDrive\EmergencyComApps\data\dimension_data.json')


#Creates four lists, the app names, the links to the apps, empty country codes list,
#and an empty app ID list later filled with the IOS app store IDs respectively. 
app_name_list = list(ios_excel['App-Name'])

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=.1, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]



definition=""
output=list()
review=ios_review_collection.find({"app_name":"FEMA"})
for x in review:
    output.append(x)

for i in range (0,2):
#app_name_list:
    prompt= f"""
    List each of app reviews below denoted with <>.\
    Reviews:<{output[0]}>
    If they are in a different language, translate them to the english language.
    Provide your response in the following format:
    App Name:
    -------------------
    app name here
    -------------------
    Review Rating:
    -------------------
    review score here
    -------------------
    Review:
    -------------------
    review here
    -------------------
    Summary:
    -------------------
    shortest summary of the review possible here

    Afterwards, state if the review of the app covers any of the following concepts, denoted by ~~ below, on a scale of 1-100, 
    100 meaning the review strongly touches on the concept.
    ~{definition}~
    """
    print(prompt)
    response=get_completion(prompt)
    print(response+"\n")
    

client.close()
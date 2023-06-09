import openai
from scraper_ios import reqListGenerator
import pandas as pd
import pymongo
from pymongo import MongoClient
import os
import json
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
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]
output=list()
review=ios_review_collection.find({"app_name":"FEMA"},{"_id":0,"content":1})
for x in review:
    output.append(x)

definition= [
	{
  	"Dimension": "Transparent Interaction",
  	"Definition": "Is the extent to which users can easily access and interact with the app without any obstacles.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Activation",
      	"Definition": "The app's ability to quickly alert users when they receive an emergency notification."
    	},
    	{
      	"Sub-Dimension": "Saliency",
      	"Definition": "The app's ability to alert users based on the type and severity of the emergency."
    	},
    	{
      	"Sub-Dimension": "Usability",
      	"Definition": "The app is ease to use, accessible, and respond quickly when the users interacts with it."
    	},
    	{
      	"Sub-Dimension": "Deep Trust",
      	"Definition": "Users' confidence in the app's underlying structure, such as its codebase, ensuring no privacy violations or tracking."
    	}
  	]
	},
	{
  	"Dimension": "Representational Fidelity",
  	"Definition": "The extent to which notifications accurately represent emergencies to users.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Currency",
      	"Definition": "Providing users with up-to-date information about emergencies and the actions to take."
    	},
    	{
      	"Sub-Dimension": "Completeness",
      	"Definition": "Ensuring users have a comprehensive representation of emergencies and the necessary counteractions."
    	},
    	{
      	"Sub-Dimension": "Exactitude",
      	"Definition": "Delivering correct and precise information about emergencies and the corresponding actions to take."
    	},
    	{
      	"Sub-Dimension": "Consistency",
      	"Definition": "Maintaining coherence in the representations of emergencies and the recommended counteractions."
    	},
    	{
      	"Sub-Dimension": "Relevance",
      	"Definition": "Providing users with representations of non-trivial emergencies that pose immediate threats."
    	},
    	{
      	"Sub-Dimension": "Representational Trust",
      	"Definition": "Building users' confidence in the accuracy of representations and the effectiveness of the suggested counteractions."
    	}
  	]
	},
	{
  	"Dimension": "Situational Awareness",
  	"Definition": "The extent to which information in the alert message enables users to take effective actions.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Promptness",
      	"Definition": "Enabling users to quickly take protective actions based on the provided information."
    	},
    	{
      	"Sub-Dimension": "Actionability",
      	"Definition": "Offering users actionable recommendations to respond to emergencies in their environment."
    	},
    	{
      	"Sub-Dimension": "Situational Trust",
      	"Definition": "Instilling in users the belief that they can effectively carry out projected actions by relying on the information from the emergency notification."
    	}
  	]
	}
  ]

#app_name_list:
prompt= f"""
    Review all of the app reviews below denoted with <>.\
    Reviews:<{output[0]},{output[1]}>
    If they are in a different language, translate them to the english language.

    

    Afterwards, based on the review contents determine how strongly the app relates to the concepts and their provided definitions denoted below with ~~,
    on a scale of 0 to 100.
    ~{definition}~
    Mark your answer with the following format seperately for each review for all dimensions and subdimensions listed:
    Review Text
    -------------------------------------
    Dimension Title,Numerical Score
    Sub-Dimension Title,Numerical Score
    -------------------------------------
    """
print(prompt)
response=get_completion(prompt)
print(response+"\n")
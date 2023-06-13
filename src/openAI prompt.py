import openai
from scraper_ios import reqListGenerator
import pandas as pd
import pymongo
from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#Establishes connection to mongo DB
mongoDBkey=os.getenv("MONGO_KEY")
client = MongoClient(mongoDBkey)

#Selects EmergencyReviewDB as the database in Mongo to populate
mongoDBdatabase=os.getenv("DATABASE")
ios_proj_db=client[mongoDBdatabase]

#Connects to desired collection in aforementioned DB
mongoDBcollection=os.getenv("COLLECTION")
review_collection = ios_proj_db[mongoDBcollection]

#Setting open API key
open_AI_Key=os.getenv("OPEN_AI_KEY")
openai.api_key=(open_AI_Key)

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]
output=list()
review=review_collection.find({"app_name":"FEMA"},{"_id":0,"content":1})
for x in review:
	if (x['content']!=None):
		if(len(x['content'])>25):
			output.append(x['content'])
    

definition=[
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
    Dimension Title,Numerical Score
    Sub-Dimension Title,Numerical Score
    
    Afterwards, convert this to a JSON file format.
    
    Only return the json format.
    
    """
print("Generating response from prompt")
response=get_completion(prompt)
print("Response:")
print(response+"\n")



# Specify the file path where you want to save the JSON file
file_path = "./Generated Files/open_AI_output.json"

# Write the OpenAI output to a JSON file
with open(file_path, 'w') as json_file:
    json.dump(json.loads(response), json_file, indent=4)
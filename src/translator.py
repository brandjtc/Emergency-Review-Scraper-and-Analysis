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
    while tempAppList[i]==None:
        i+=1
    return translation.detect(tempAppList[i]["review"]).lang

def langDetectorAndroid():
    # Pulls reviews from the database
    reviews = list(review_collection.find())
    for review in reviews:
        content = review.get('content')
        translated = review.get('translated')  # Get the 'translated' field
        if content:
            if translated is None:
                # Create the 'translated' field if it doesn't exist in the document
                translated = False
                review_collection.update_one(
                    {"_id": review['_id']},
                    {"$set": {"translated": translated}}
                )
            if not translated:
                detection = translation.detect(content).lang
                if detection != "en":
                    translated_content = translateToEng(content)
                    # Update the review in the database with the translated content and set 'translated' to True
                    review_collection.update_one(
                        {"_id": review['_id']},
                        {"$set": {
                            "translated_content": translated_content,
                            "language": detection,
                            "translated": True
                        }}
                    )
                    print(f"Translated review: {review['_id']}")
    print("Translation complete")



if __name__ == '__main__':
    langDetectorAndroid()
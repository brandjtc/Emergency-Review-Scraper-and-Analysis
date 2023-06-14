import os
from pymongo import MongoClient
from deep_translator import GoogleTranslator
from langdetect import detect
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Establishes connection to MongoDB
client = MongoClient(os.getenv("MONGO_KEY"))
db = client[os.getenv("DATABASE")]
review_collection = db[os.getenv("COLLECTION")]

# Function that translates the detected text and returns it in english
def translate_text(text):
    translator = GoogleTranslator(source='auto', target='en')
    translated_text = translator.translate(text)
    return translated_text

# Function detects the language using langdetect
def detect_language(text):
    language = detect(text)
    return language

def process_review(review):

    content = review.get('content')
    translated = review.get('translated')
    
    # The review has to have 2 characters at the minimum to be translated
    if content and len(content) > 2:
        if not translated:
            # A try-except to use the language detection and then process the reviews by calling translate_text
            try:
                language = detect_language(content)
                print(f"Processing review: {review['_id']}")
                print("Content:", content)
                print("Detected language:", language)
                
                if language and language != "unknown" and language != "un" and language != "en":
                    translated_content = translate_text(content)
                    review_collection.update_one(
                        {"_id": review['_id']},
                        {"$set": {
                            "translated_content": translated_content,
                            "language": language,
                            "translated": True
                        }}
                    )
                else:
                    print(f"Language detection skipped for review: {review['_id']}")
            except Exception as e:
                print(f"Language detection error occurred: {e}")

def lang_detector_android():
    reviews = list(review_collection.find())
    
    for review in reviews:
        process_review(review)
    
    print("Translation complete")

if __name__ == '__main__':
    lang_detector_android()

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

def translate_text(text):
    translator = GoogleTranslator(source='auto', target='en')
    translated_text = translator.translate(text)
    return translated_text

def detect_language(text):
    language = detect(text)
    return language

def process_review(review):
    content = review.get('content')
    translated = review.get('translated')
    
    if content and len(content) > 3:
        if translated is None or (translated and review.get('language') == 'en'):
            review_collection.update_one(
                {"_id": review['_id']},
                {"$set": {
                    "translated": False,
                    "translated_content": "None"
                }}
            )
        if not translated:
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
                    print(f"Translated review: {review['_id']}")
                else:
                    print(f"Language detection skipped for review: {review['_id']}")
            except Exception as e:
                print(f"Language detection error occurred: {e}")

def lang_detector_android():
    reviews = list(collection.find())
    
    for review in reviews:
        process_review(review)
    
    print("Translation complete")

if __name__ == '__main__':
    lang_detector_android()

import pandas as pd
import mongoDB_settings as mongDB
import FormatFile as ff
import coreModule as cm
import os
import json
import pickle
import time
from dotenv import load_dotenv, find_dotenv
import openAI_settings as ai
_ = load_dotenv(find_dotenv()) 

# Setting constants
SINGLEINPUT = False
RESET = False
SLEEPTIME = 20

# Define file paths
GENERATED_FILES_DIR = os.path.join(os.path.dirname(__file__), 'Generated Files')
REVIEWS_AP_DIR = os.path.join(GENERATED_FILES_DIR, 'Reviews_AP')
RESPONSES_AP_DIR = os.path.join(GENERATED_FILES_DIR, 'Storage_AP')
EXCEL_FILE_PATH = os.path.join(RESPONSES_AP_DIR, 'Responses.xlsx')

mongoDBcollection = os.getenv("COLLECTION")
review_collection = mongDB.MongoDBsetup(mongoDBcollection)

# Setting OpenAI key
open_AI_Key = os.getenv("ANTH_OPEN_AI_KEY")
ai.set_API_key(open_AI_Key)

# Reads pickle using Pandas library
saved_file_path = os.path.join(GENERATED_FILES_DIR, 'review_data.pkl')
with open(saved_file_path, 'rb') as fileObj:
    data = pickle.load(fileObj)

# Extract app names and reviews from review_data
app_name_list = [review['App Name'] for review in data]
reviews_list = data

definition = ff.definition
jsonFormat = ff.jsonFormat

def aiInputHelperFunc(app_name):
    print(f"Gathering all reviews for app: {app_name}")
    app_reviews=review_collection.find({"app_name":app_name},{"_id":1,"content":1,"translated_content":1,"language":1})
    reviewStartVar = cm.reviewStoreRead(SINGLEINPUT,RESPONSES_AP_DIR,RESET)
    if RESET or reviewStartVar==None:
        print("Review Store Num reset")
        reviewStartVar=0

    print(f"Counting documents for app: {app_name}")
    maxVal=review_collection.count_documents({"app_name":app_name})
    print(f"There are {maxVal} document(s)")
    print("Preparing for insertion into OpenAI prompt")
    reviewNum = reviewStartVar

    for x in range(reviewStartVar, maxVal):
        review = app_reviews[x]
        id_str=str(review['_id'])
        if review['language'] != 'en':
            response = cm.aiInput(review['translated_content'], app_name, review['_id'], reviewNum)
            reviewStr=review['translated_content']
        else:
            response = cm.aiInput(review['content'], app_name, review['_id'], reviewNum)
            reviewStr=review['content']
        reviewNum += 1
        time.sleep(SLEEPTIME)

        # Stores what review the AI left off on if Single Input is false.
        cm.reviewStoreWrite(reviewNum,SINGLEINPUT,RESPONSES_AP_DIR)
         # Extract the nested dictionary from file_data and convert it to a list
        record = [response]

        # Initialize an empty list to hold flattened records
        flattened_records = []

        # Flatten data
        if len(response) > 0:
            # Now you can access the keys in the dictionary as expected
            flattened_record = {}
            flattened_record["ID"] = id_str
            flattened_record["Content"] = reviewStr
            flattened_record["Strongest Sub-Dimension"] = record[0]["Strongest Sub-Dimension"]
            flattened_record["Strongest Sub-Dimension Definition"] = record[0]["Strongest Sub-Dimension Definition"]
            flattened_record.update(record[0]["Transparent Interaction Sub-Dimensions"][0])
            flattened_record.update(record[0]["Representational Fidelity Sub-Dimensions"][0])
            flattened_record.update(record[0]["Situational Awareness Sub-Dimensions"][0])
            flattened_records.append(flattened_record)

            # Convert the list of dictionaries to a DataFrame
            df_nested_list = pd.DataFrame(flattened_records)

            excel_file_path = EXCEL_FILE_PATH
            if os.path.isfile(excel_file_path):
                existing_df = pd.read_excel(excel_file_path)

                # Append the new DataFrame to the existing DataFrame
                df_combined = pd.concat([existing_df, df_nested_list], ignore_index=True)

                # Then write the combined DataFrame to the Excel file
                df_combined.to_excel(excel_file_path, index=False)
            else:
                # Write the DataFrame to the Excel file
                df_nested_list.to_excel(excel_file_path, index=False)
        else:
            print("Error: Empty file_data")

def aiInput(reviewStr, app_name, id, reviewNum):
    id_str = str(id[0])
    print(f"Scoring review No.{reviewNum} for app {app_name}")

    prompt = ff.retPrompt(reviewStr)

    response = cm.get_completion(prompt, jsonFormat)
    print("Scoring complete.\n")

    filename = f"{app_name}_review_{reviewNum}.json"
    file_path = os.path.join("Generated Files", "Reviews_AP", filename)

    try:
        with open(file_path, "r") as demoFile:
            demoFile.readline()
        file_path += "_2"
    except FileNotFoundError:
        pass

    print("Formatting the response as a JSON file.")
    file_data = json.loads(response)

    # Write the OpenAI output to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(file_data, json_file, indent=4)


if __name__ == "__main__":
    if not SINGLEINPUT:
        nameList=cm.appNameListGenerate()
        appStartVar=cm.appStoreRead(SINGLEINPUT,RESPONSES_AP_DIR)
            # Storing what app the AI left off on if Single Input is false
        for i in range (appStartVar,len(nameList)):
            cm.appNameStoreWrite(i,SINGLEINPUT,RESPONSES_AP_DIR)
            aiInputHelperFunc(nameList[i])
            # Sets review back to 0 after app is done if Single Input is false.
            cm.reviewStoreWrite(0,SINGLEINPUT,RESPONSES_AP_DIR)

    # Put single apps here for single input
    if SINGLEINPUT:
        aiInputHelperFunc("FEMA")
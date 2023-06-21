#declarations
import os
from app_store_scraper import AppStore
import random
from pymongo import MongoClient
import pandas as pd
import datetime as dt
from datetime import datetime
import tzlocal as tz
from tzlocal import get_localzone
import translator as tr

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
#constants
#Set to -1 to get all reviews from an app. Otherwise, rounds up to nearest positive multiple of 20.
REVIEWBATCHCOUNT=-1
SLEEP_TIME_RANGE = (1, 2)
MANUAL_INSERT=False
TRANSLATE=False
#WARNING, IF SET TO TRUE, EMPTIES DATABASE
RESET=False
#Establishes connection to mongo DB
mongoDBkey=os.getenv("MONGO_KEY")
client = MongoClient(mongoDBkey)

#Selects EmergencyReviewDB as the database in Mongo to populate
mongoDBdatabase=os.getenv("DATABASE")
ios_project_db=client[mongoDBdatabase]

#Connects to desired collection in aforementioned DB
mongoDBcollection=os.getenv("COLLECTION")
review_collection = ios_project_db[mongoDBcollection]

excelFilePath=os.getenv("EXCELFILEPATH")
#Reads excel doc using Pandas library
ios_excel=pd.read_excel(excelFilePath,usecols='A,L')

if RESET==True:
    print("Restart scraper from scratch, WIPING ALL IOS REVIEWS IN THE PROCESS?")
    userInp=input("Y/N: ")
    while (userInp.lower()!='y' and userInp.lower()!='n'):
        print("Invalid user input.\n")
        print("Restart scraper from scratch, WIPING ALL IOS REVIEWS IN THE PROCESS?")
        userInp=input("Y/N: ")
    if userInp.lower()=='y':
        review_collection.delete_many({"platform":"Apple App Store"})
        print("All IOS reviews deleted")
    else:
        print("Reset process stopped. Set RESET constant variable to false to prevent this popup.")


    
#Creates four lists, the app names, the links to the apps, empty country codes list,
#and an empty app ID list later filled with the IOS app store IDs respectively. 
app_name_list = list(ios_excel['App-Name'])
app_links_raw_data = list(ios_excel['Link to App Store'])
app_id_list=list()
country_code_list=list()

def reviewStoreWrite(reviewNum):
    with open(os.getenv("STORFILELOC"),'w') as storeFile:
        storeFile.write(str(reviewNum))

def reviewStoreRead():
    try:
        with open(os.getenv("STORFILELOC"),'r') as readFile:
            testNum=readFile.readline()
            if testNum.isnumeric():
                return int(testNum)
    except FileNotFoundError:
        pass
    return 0

def reqListGenerator():
    for i in range(0,len(app_name_list)):
    #1):
        temp="NA"
        #The link is converted to a string for this conditional to make it easier to process NAs,
        #when there is no link. 
        if (str(app_links_raw_data[i])!="nan"):
            tempSplit = app_links_raw_data[i].split("/")
            countryCode=tempSplit[3]             
            idSplit=tempSplit[6].split("d")

            #If statement checks for lingering language tag in the ID extracted from the app link. 
            #If present, it is removed and the temp variable is adtempApp.reviews[j]usted accordingly to be added to the app ID list.
            if ("?" in idSplit[1]):
                idSplit=idSplit[1].split("?")
                temp=idSplit[0]
            else:
                temp = idSplit[1]
        #Appends ID to the list. If there is no ID in the Apple app store, NA is added as the ID instead.
        #Same system with country codes
        app_id_list.append(temp)
        country_code_list.append(countryCode)

#Function that scrapes reviews off of Apple App Store using app_store_scraper library
def reviewScraper(num):
    app_name=app_name_list[num]
    app_id=app_id_list[num]
    country_code=country_code_list[num]

    #Deletes all records of app inside database if Manual Insertion is set by user
    if (MANUAL_INSERT==True):
        ios_project_db.review_collection.delete_many({"app_name":app_name_list[num],"platform":"Apple App Store"})

    if (country_code!='NA')&(app_id!='NA'):
        #Details what app is currently being scrapped and the start time/date.
        print("Review scraping for app: "+app_name)
        print(f"App ID: {app_id}")
        print(f"App is number {num} on the excel document")
        fmt = "%m/%d/%y - %T %p"  
        start= dt.datetime.now(tz=get_localzone())
        print("Began at:"+start.strftime(fmt))
        #Puts the app information into the tempApp container to later generate reviews.
        tempApp=AppStore(country_code,app_name,app_id)
        #Generates reviews using app stored in the tempApp container. Constant variables edit functionality
        # present here to alter amount of reviews grabbed.
        if (REVIEWBATCHCOUNT!=-1):
            tempApp.review(how_many=REVIEWBATCHCOUNT,sleep=random.randint(*SLEEP_TIME_RANGE))
        else:
            tempApp.review(sleep=random.randint(*SLEEP_TIME_RANGE))
        print("-"*40)
        print("Preparing fetched reviews for integration into the database for app "+app_name)
        
        #Variable declaration
        toTranslate=False

        #Checks language of upcoming app reviews and decides if they should be translated
        lang=tr.langDetectorIOS(tempApp.reviews)
        if lang!="en":
            toTranslate=True
        if lang=="break":
            print("Error response. Try Again Later.")

        #Nested for loop that converts the   library's output into one suitable
        #for the Mongo database.
        reviewStartVar=reviewStoreRead()
        for j in range(reviewStartVar,len(tempApp.reviews)):
            #Stores index value of next review in case program is interrupted.
            reviewStoreWrite(j)
            if (app_id!="NA")&(app_id!=""):
                #Empty list created to use as container for adtempApp.reviews[j]usted scraper output
                tempDiction={}

                #if statements intended to add flexibility to the code accounting for all possible permutations a user may want
            
                if TRANSLATE==True&toTranslate==True:
                    tempDiction.update([("userName",tempApp.reviews[j]["userName"]),
                                    ("title",tempApp.reviews[j]["title"]),
                                    ("content",tempApp.reviews[j]["review"]),
                                    ("score",tempApp.reviews[j]["rating"]),("at",tempApp.reviews[j]["date"]),
                                    ("app_name",app_name),("app_id",app_id),
                                    ("platform","Apple App Store"),("language",lang),
                                    ("translated",True),
                                    ("translated_title",tr.translateToEng(tempApp.reviews[j]["title"])),
                                    ("translated_content",tr.translateToEng(tempApp.reviews[j]["review"]))])
            
                else:
                    tempDiction.update([("userName",tempApp.reviews[j]["userName"]),
                                ("title",tempApp.reviews[j]["title"]),
                                ("content",tempApp.reviews[j]["review"]),
                                ("score",tempApp.reviews[j]["rating"]),
                                ("at",tempApp.reviews[j]["date"]),
                                ("app_name",app_name),("app_id",app_id),
                                ("platform","Apple App Store"),("language",lang),
                                ("translated",False),("translated_title",None),("translated_content",None)])
               
                #Inserting into mongoDB database
                print(f"Uploading Review #: {j}")
                review_collection.insert_one(tempDiction)
        #Sets review num back to 0 after scraping is finished.        
        reviewStoreWrite(0)

        #Details end time and time elapsed.
        print("-"*40)
        print("Review scraping finished for app: "+app_name)
        fmtend = "%m/%d/%y - %T %p"  
        end= dt.datetime.now(tz=get_localzone())
        print("Ended at: "+end.strftime(fmtend))
        print(f"Time elapsed: {end - start}")
        print("-"*40)

#Helper function that calles review scraper function to be done for all apps in app name list.
def reviewScraperHelper():
    for i in range(0,len(app_name_list)):
        if review_collection.find_one({'app_name':app_name_list[i],'platform':"Apple App Store"}) is None:
            reviewScraper(i)


if __name__ == "__main__":
    #Generates app name list.
    reqListGenerator()
    #Storage file stores where scraper left off if interrupted.     

    #for if user wants to manually add apps using code.

    if (MANUAL_INSERT==False):
        reviewScraperHelper()
    elif (MANUAL_INSERT==True):
        reviewScraper("App Name Here")
    client.close()
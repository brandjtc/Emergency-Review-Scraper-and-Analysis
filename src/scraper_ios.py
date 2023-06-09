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
AUTO=False
#MANUAL_INSERT takes precedence over AUTO
MANUAL_INSERT=False
TRANSLATE=True

#Establishes connection to mongo DB
mongoDBkey=os.getenv("MONGO_KEY")
client = MongoClient(mongoDBkey)

#Selects EmergencyReviewDB as the database in Mongo to populate
mongoDBdatabase=os.getenv("DATABASE")
ios_proj_db=client[mongoDBdatabase]

#Connects to desired collection in aforementioned DB
mongoDBcollection=os.getenv("COLLECTION")
review_collection = ios_proj_db[mongoDBcollection]

excelFilePath=os.getenv("EXCELFILEPATH")
#Reads excel doc using Pandas library
ios_excel=pd.read_excel(excelFilePath,usecols='A,L')


#Creates four lists, the app names, the links to the apps, empty country codes list,
#and an empty app ID list later filled with the IOS app store IDs respectively. 
app_name_list = list(ios_excel['App-Name'])
app_links_raw_data = list(ios_excel['Link to App Store'])
app_id_list=list()
country_code_list=list()

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
            #If present, it is removed and the temp variable is adjusted accordingly to be added to the app ID list.
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
        ios_proj_db.review_collection.delete_many({"app_name":app_name_list[num],"platform":"Apple App Store"})

    if (country_code!='NA')&(app_id!='NA'):
        #Details what app is currently being scrapped and the start time/date.
        print("Review scraping for app: "+app_name)
        fmt = "%m/%d/%y - %T %p"  
        start= dt.datetime.now(tz=get_localzone())
        print("Began at:"+start.strftime(fmt))
        #Puts the app information into the tempApp container to later generate reviews.
        print(f"App ID: {app_id}")
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
        #container for future reviews
        reviewContainer=list()

        #Nested for loop that converts the   library's output into one suitable
        #for the Mongo database.
        for j in range (0,len(tempApp.reviews)):
            if (app_id!="NA")&(app_id!=""):
                dictionaryTemp=list(tempApp.reviews[j].items())

                #Empty list created to use as container for adjusted scraper output
                tempDiction={}

                #if statements intended to add flexibility to the code accounting for all possible permutations a user may want
                if TRANSLATE==True&toTranslate==True:
                    tempDiction.update([(dictionaryTemp[4]),(dictionaryTemp[5]),
                                    ("title",tr.translateToEng(tempApp.reviews[j]["title"])),
                                    ("untranslated_title",tempApp.reviews[j]["title"]),
                                    ("content",tempApp.reviews[j]["review"]),
                                    ("translated_content",tr.translateToEng(tempApp.reviews[j]["review"])),
                                    ("score",tempApp.reviews[j]["rating"]),("at",tempApp.reviews[j]["date"]),
                                    ("app_name",app_name),("app_id",app_id),
                                    ("platform","Apple App Store"),("language",lang),("translated",True)])
            
                else:
                    tempDiction.update([(dictionaryTemp[4]),(dictionaryTemp[5]),
                                ("title",tempApp.reviews[j]["title"]),("untranslated_title",None),
                                ("content",tempApp.reviews[j]["review"]),("translated_content",None),
                                ("score",tempApp.reviews[j]["rating"]),("at",tempApp.reviews[j]["date"]),
                                ("app_name",app_name),("app_id",app_id),("platform","Apple App Store"),
                                ("language",lang),("translated",False)])
                    
                #Packing into container for insertion into MongoDB database
                reviewContainer.append(tempDiction)
        try:
            review_collection.insert_many(reviewContainer) 
        except TypeError:
            print("NOTE:\nThis application has no reviews available")

        #Details end time and time elapsed.
        print("-"*40)
        print("Review scraping finished for app: "+app_name)
        fmtend = "%m/%d/%y - %T %p"  
        end= dt.datetime.now(tz=get_localzone())
        print("Ended at: "+end.strftime(fmtend))
        print(f"Time elapsed: {end - start}")
        print("-"*40)
        
        #Single insert variable for adding only a single app's reviews.
        if (MANUAL_INSERT==False):
            #Stores index value of the current app in case program is interrupted.
            print(f"Storage var incremented: {num+1}")
            storeFile= open(os.getenv("STORFILELOC"),"w+")
            storeFile.write(str(num+1))
            storeFile.close()

#Helper function that calles review scraper function to be done for all apps in app name list.
def reviewScraperHelper(num):
    for i in range(num,len(app_name_list)):
        reviewScraper(i)


if __name__ == "__main__":
    #Generates app name list.
    reqListGenerator()
    #Storage file stores where scraper left off if interrupted.     

    #for if user wants to manually add apps using code.

    if (MANUAL_INSERT==False):
    #Automatic behavior that starts from the beginning if auto is True. Wipes all apple apps from database.
        if (AUTO==True):
            print("AUTO MODE ENABLED")
            review_collection.delete_many({"platform":"Apple App Store"})
            reviewScraperHelper(0)

        #Behavior for if AUTO is set to false
        else:
            storageNum=0
            checkFile = open(os.getenv("STORFILELOC"),"r")
            testNum=checkFile.readline()
            if testNum.isalnum():
                storageNum=int(testNum)   
            checkFile.close()
            #checks if storageNum has been incremented.
            if storageNum!=0:
                #If it does, sets the number stored inside as the index of which app to start
                # review scraping from if user chooses to with a y/n prompt.
                userInput=input((f"If you want to run the scraper starting from app {app_name_list[storageNum]}, type 'y'\nIf you want to run the scraper from beginning and delete all current entries, type 'n'\ny/n: "))

                #Input validation while loop.
                while (userInput.lower()!="y")&(userInput.lower()!="n"):
                    print("Incorrect formatting")
                    userInput=input((f"If you want to run the scraper starting from app {app_name_list[storageNum]}, type 'y'\nIf you want to run the scraper from beginning and delete all current entries, type 'n'\ny/n: "))
                
                #For if user chooses yes.
                if (userInput.lower()=='y'):
                    print("Preparing for insertion into MongoDB")
                    delList=list()
                    for i in range(storageNum,len(app_name_list)):
                        review_collection.delete_many({"app_name":app_name_list[i],"platform":"Apple App Store"})
                    reviewScraperHelper(storageNum)
                #For if user chooses no.
                else:
                    review_collection.delete_many({"platform":"Apple App Store"})
                    reviewScraperHelper(0)
            #For if file is empty.
            else:
                print("FILE EMPTY OR SET TO 0. AUTO MODE ENABLED")
                review_collection.delete_many({"platform":"Apple App Store"})
                reviewScraperHelper(0)
    client.close()
To make the IOS scraper run, the following libraries installations are necessary:
```
!pip install app_store_scraper
!pip install pandas
!pip install pymongo
```

Now that the required libraries are installed, we can improt them into our python file. Random is native to python and does not need to be pip installed.
```python
import pandas as pd
from pymongo import MongoCLient
import random
from app_store_scraper import AppStore
```

Next, constant variables should be set. REVIEWBATCHCOUNT sets how many reviews should be gathered from each app, to the nearest multiple of 20. E.G., 1 gives 20 reviews and 38 gives 40 reviews. Setting this value to -1 will give all reviews for an app.

Sleep time range tells the review scraper how long it should wait between reviews to scrape more. Currently, it waits 1-2 seconds between batches using a range of 1-2.
```python
REVIEWBATCHCOUNT=-1
SLEEP_TIME_RANGE = (1, 2)
```
Now, you just have to connect to a MongoDB database and collection. You will need your SRV connection string from MongoDB to integrate properly with python. 
```python
#Establishes connection to mongo DB
client = MongoClient("mongoDBconnectionStringHere")
```

Next you have to specify which database you want to connect to by name
```python
#Selects EmergencyReviewDB as the database in Mongo to populate
ios_proj_db=client["mongoDBdatabaseHere"]

#Connects to desired collection in aforementioned DB
review_collection = ios_proj_db["mongoDBcollectionHere"]
```

Now, pandas is used to read an excel document. The scraper requires an App Name and an IOS app store Link to run, which are found under appropriately labelled columns in the [Excel Spreadsheet](https://github.com/brandjtc/Emergency-Review-Scraper-and-Analysis/blob/main/data/EmergencyComData.xlsx). In addition, the .head function is used just to make sure the we're pulling the right data.
```python
ios_excel=pd.read_excel("excelFilePathHere")
app_df.head()
```

Four lists are created. One containing the app name, one containing a list of the app links, and then two empty lists to be filled in the next step with information extracted from the app link.
```python
#Creates four lists, the app names, the links to the apps, empty country codes list,
#and an empty app ID list later filled with the IOS app store IDs respectively. 
app_name_list = list(ios_excel['App-Name'])
app_links_raw_data = list(ios_excel['Link to App Store'])
app_id_list=list()
country_code_list=list()
```

The reqListGenerator function is used to extract the remaining necessary data, being the app ID and country code, from the app link. It does this by splitting strings at certain breakpoints and adding this data to empty lists for later use.
```python
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
```

Next up is the main review scraper function. It can be a little unwieldy so the explanation will be broken up into segments.
First up is the helper function. This takes an index of the desired starting app from the app name list and starts a for loop that repeatedly calls the main scraper function. This makes the code more modular and still allows for the scraping of single specific apps via user intervention without major code rewrites.
```python
def reviewScraperHelper(num):
    for i in range(num,len(app_name_list)):
        reviewScraper(i)
```

The index passed in from the helper function enters the main reviewScraper function and pulls the information from all the previously crafted lists needed to start scraping, namely the App Name, App ID on the IOS app store, and the country code.
```python
#Function that scrapes reviews off of Apple App Store using app_store_scraper library
def reviewScraper(num):
    app_name=app_name_list[num]
    app_id=app_id_list[num]
    country_code=country_code_list[num]
```

Next, an if statement runs to check if the country code or the App ID is NA. If this is is the case, that specific app is skippd over.
```python
    if (country_code!='NA')&(app_id!='NA'):
        #Details what app is currently being scrapped and the start time/date.
        print("Review scraping for app: "+app_name)

        #Puts the app information into the tempApp container to later generate reviews.
        print(f"App ID: {app_id}")
        tempApp=AppStore(country_code,app_name,app_id)
        #Generates reviews using app stored in the tempApp container. Constant variables edit functionality
        # present here to alter amount of reviews grabbed.
```

Afterwards, an if statement checks the value of REVIEWBATCHCOUNT. As previously stated, it being set to -1 fetches all reviews, while it being any other number fetches a review amount equal to the nearest positive multiple of 20.
```python
        if (REVIEWBATCHCOUNT!=-1):
            tempApp.review(how_many=REVIEWBATCHCOUNT,sleep=random.randint(*SLEEP_TIME_RANGE))
        else:
            tempApp.review(sleep=random.randint(*SLEEP_TIME_RANGE))
        print("-"*40)
        print("Preparing fetched reviews for integration into the database for app "+app_name)
```

Then, a container variable is declared to house all gathered reviews. A for loop is made that cycles through the list of dictionaries, adressable via tempApp.reviews, forming all available data about every review. This data is then adjusted slightly to fit the desired format of the MongoDB collection
```python
        #container for future reviews
        reviewContainer=list()

        #Nested for loop that converts the app_store_scraper library's output into one suitable
        #for the Mongo database.
        for j in range (0,len(tempApp.reviews)):
            if (app_id!="NA")&(app_id!=""):
                dictionaryTemp=list(tempApp.reviews[j].items())

                #Empty list created to use as container for adjusted scraper output
                tempDiction={}
                tempDiction.update([(dictionaryTemp[4]),(dictionaryTemp[5]),("title",tempApp.reviews[j]["title"]),
                            ("content",tempApp.reviews[j]["review"]),("score",tempApp.reviews[j]["rating"]),
                            ("at",tempApp.reviews[j]["date"]),("app_name",app_name),
                            ("app_id",app_id),("platform","Apple App Store"))
                    
                #Packing into container for insertion into MongoDB database
                reviewContainer.append(tempDiction)
                
```

Finally, after all the reviews are converted into the desired format and packed into the review container list, they are inserted all at once into the mongoDB database.
```python
        review_collection.insert_many(reviewContainer)     
        print("-"*40)
        print("Review scraping finished for app: "+app_name)
        print("-"*40)
```

All that's left is the main function that runs only if the .py file containing the review scraper function is the primary file being run.
This main calls upon the reqListGenerator function to set up the required lists for the app scraper to run, calls upon the helper function to run the app scraper with a for loop that iterates through every app, and then closes the connection to MongoDB.
```python
if __name__ == "__main__":
    #Generates app name list.
    reqListGenerator()
    reviewScraperHelper(0)
    #Terminates connection to mongo db client.
    client.close()

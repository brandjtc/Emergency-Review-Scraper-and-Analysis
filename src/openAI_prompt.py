import mongoDB_settings as mongDB
import coreModule as cm
import openAI_settings as ai
import os
import time
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

#Setting constants for program modularity
SINGLEINPUT=False
RESET=True
FILEPATH="./Generated Files/Storage Files BR/"
SLEEPTIME=20

#Setting open AI key
open_AI_Key=os.getenv("BRAND_OPEN_AI_KEY")
ai.set_API_key(open_AI_Key)

#Function that sets up MongoDB collection for query, insertion & deletion
currentCollection=os.getenv("COLLECTION")
review_collection=mongDB.MongoDBsetup(currentCollection)

#Reads excel doc using Pandas library
app_name_list=cm.appNameListGenerate()

#Data preparation function that then feeds directly into OpenAI Input function.
def aiInputHelperFunc(app_name):

	print(f"Gathering all reviews for app: {app_name}")

	#mongoDB query gathering all reviews for Open AI analysis for a given app.
	review=review_collection.find({"app_name":app_name},{"_id":1,"content":1,"translated_content":1,"language":1})

	#Reads review storage file to find what review was left off on.
	reviewStartVar=cm.reviewStoreRead(SINGLEINPUT,FILEPATH,RESET)

	#Counting how many documents a given app has is needed to know when the for loop below should stop
	print(f"Counting documents for app:{app_name}")
	maxVal=review_collection.count_documents({"app_name":app_name})
	print(f"There are {maxVal} document(s)")

	print("Preparing for insertion into OpenAI prompt")
	reviewNum=reviewStartVar

	#For loop that cycles through the stored value that was left off on and the total document count.
	#It calls the AI input function to generate a response for each document.
	for x in range(reviewStartVar,maxVal):
		if (review[x]['content']!=None) and (len(review[x]['content'])>25):
			if review[x]['language']=="en":
				response=cm.aiInput(review[x]['content'],app_name,[review[x]['_id']],reviewNum)
			else:
				response=cm.aiInput(review[x]['translated_content'],app_name,[review[x]['_id']],reviewNum)

			#Generates the file name.
			cm.fileGeneration(response,reviewNum,app_name,FILEPATH)

			#Sleeping to avoid free limit of OpenAI
			print("Mandatory 20sec wait")
			time.sleep(SLEEPTIME)

		#Review number ticks up after every review is scored.
		reviewNum+=1

		#Stores what review the AI left off on if Single Input is false.
		cm.reviewStoreWrite(reviewNum,SINGLEINPUT,FILEPATH)
		
if __name__ == "__main__":
	if (SINGLEINPUT!=True):

		#Reads the app storage value. It returns None/Null if nothing is present
		appStartVar=cm.appStoreRead(SINGLEINPUT,FILEPATH)

		#Sets value to 0 if None value is returned or reset is active.
		if RESET==True:
			appStartVar=0
		for j in range(appStartVar,len(app_name_list)):
			#Storing what app the AI left off on if Single Input is false
			cm.appNameStoreWrite(j,SINGLEINPUT,FILEPATH)
			aiInputHelperFunc(app_name_list[j])
			
			#Sets review back to 0 after app is done if Single Input is false.
			cm.reviewStoreWrite(0,SINGLEINPUT,FILEPATH)
		#Resetting App Name Store to 0 after program completion
		cm.appNameStoreWrite(0,SINGLEINPUT,FILEPATH)

	#Put single apps here for single input
	if (SINGLEINPUT==True):
		aiInputHelperFunc("FEMA")
from googletrans import Translator

translation=Translator()

#Translates string to English
def translateToEng(string):
    returnVal=translation.translate(string,dest='en')
    return returnVal.text

def langDetectorIOS(tempAppList):
    i=0
    while tempAppList[i]==None:
        i+=1
    return translation.detect(tempAppList[i]["review"]).lang

def langDetectorAndroid(tempAppList):
    i=0
    while tempAppList[i]==None:
        i+=1
    return translation.detect(tempAppList[i]["content"]).lang
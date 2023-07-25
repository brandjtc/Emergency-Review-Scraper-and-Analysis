import openAI_settings as ai
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


#Setting open AI key
open_AI_Key=os.getenv("BRAND_OPEN_AI_KEY")
ai.set_API_key(open_AI_Key)

prompt=f"""Consider the following definition of a construct called transparent interaction":
Transparent Interaction is the affordance for the user to interact with the mobile alert app timely and unimpeded by the app interface or the physical characteristics of their mobile device.
Then consider the four following definitions of its possible subdimensions:
1. Activation is the affordance for the user to gain a state of alertness within a useful timeframe upon receiving an emergency notification from the mobile alert app. 
2. Saliency is the affordance for the user to gain a state of alertness congruent with the type of emergency and its severity upon receiving an emergency notification from the mobile alert app.
3. Usability is the affordance for the user to interact with the mobile alert app easily (e.g., no delays; quick response time; accessible)
4. Deep trust is the affordance to increase the user's level of confidence that the application is designed to support only its intended use (e.g., no trackers, no violations of privacy). "Deep" trust refers to trust in elements of the system's deep structure, such as its codebase.

Create more subdimensions that fit to the definition of "transparent interaction" """

print(ai.get_completion(prompt))
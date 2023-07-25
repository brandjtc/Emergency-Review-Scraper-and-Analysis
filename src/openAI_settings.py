import openai
import time
import pymongo

#Setting Open Ai Key
def set_API_key(open_AI_Key):
	openai.api_key=(open_AI_Key)

#Sets model and temperature for returned Chat GPT response.
def get_completion(prompt, model="gpt-3.5-turbo"):
    try:
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message["content"]
    except openai.error.ServiceUnavailableError:
         print("OPENAI server down. waiting 5 seconds")
         time.sleep(5)
         return get_completion(prompt,model="gpt-3.5-turbo")
    except openai.error.APIConnectionError:
         print("Lost connection to OPENAI server. waiting 5 seconds")
         time.sleep(5)
         return get_completion(prompt,model="gpt-3.5-turbo")
    except pymongo.errors.AutoReconnect:
        print("Pymongo lost connection to DB")
        time.sleep(5)
        return get_completion(prompt,model="gpt-3.5-turbo")


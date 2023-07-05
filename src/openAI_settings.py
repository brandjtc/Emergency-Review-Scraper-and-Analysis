import openai

#Setting Open Ai Key
def set_API_key(open_AI_Key):
	openai.api_key=(open_AI_Key)

#Sets model and temperature for returned Chat GPT response.
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


import openai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("API_KEY")
openai.api_key = API_KEY

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model = "gpt-4-32k",
        messages = [{"role":"user","content":prompt}]
    )
    return response
    # return response.choices[0].message.content.strip()

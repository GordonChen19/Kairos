from openai import OpenAI

from dotenv import load_dotenv
import os

load_dotenv()

GPT_API = os.getenv('GPT_API')

client = OpenAI(api_key=GPT_API)




def chat_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
    messages=messages,
    temperature=0)
    return response.choices[0].message.content



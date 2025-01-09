from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from openai import OpenAI
from fastapi import FastAPI


from typing import Union
import tweepy
from config import CONSUMER_SECRET, CONSUMER_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY
from fastapi import FastAPI
from openai import OpenAI

app = FastAPI()
client = OpenAI(
  api_key=API_KEY
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message.content)

# Define tools for agent to use
@tool
def search(query: str):
    """Call to surf the web"""
     # This is a placeholder
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

tools = []

auth = tweepy.OAuth1UserHandler(
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)

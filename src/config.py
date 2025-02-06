import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from src.agent_personality import get_system_message
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential
import time


load_dotenv()


url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

#twitter api
TWITTER_AUTH_CONSUMER_KEY = os.getenv("TWITTER_AUTH_CONSUMER_KEY")
TWITTER_AUTH_CONSUMER_SECRET = os.getenv("TWITTER_AUTH_CONSUMER_SECRET")
TWITTER_AUTH_BEARER_TOKEN = os.getenv("TWITTER_AUTH_BEARER_TOKEN")
TWITTER_AUTH_ACCESS_TOKEN = os.getenv("TWITTER_AUTH_ACCESS_TOKEN")
TWITTER_AUTH_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_AUTH_ACCESS_TOKEN_SECRET")

# openai api
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_CLIENT_ID = os.getenv("CLIENT_ID")
# OPENAI_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# tavily api key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# Configure AI model and memory
model = ChatOpenAI(
    model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY, temperature=0.7
).with_config({"run_name": "RecluseAI"})

memory = MemorySaver()
thread_id = "test_thread"
config = {"configurable": {"thread_id": thread_id}}


# Agent setup
agent_executor = create_react_agent(
    tools=[],
    model=model,
    checkpointer=memory,
    state_modifier=get_system_message("humour"),
)


last_request_time = time.time()
REQUEST_INTERVAL = 5  # 5 seconds between requests

# Exponential backoff: Retries up to 5 times with increasing delays (1s, 2s, 4s, 8s...)
@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
def call_openai(prompt):
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=config
    )
    return response

def call_openai_with_throttling(prompt):
    global last_request_time

    # Ensure a gap between API calls
    time_since_last_request = time.time() - last_request_time
    if time_since_last_request < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - time_since_last_request)

    last_request_time = time.time()
    return call_openai(prompt)  # Call OpenAI with retry logic
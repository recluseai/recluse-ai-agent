import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from src.agent_personality import get_system_message
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

#twitter api
TWITTER_AUTH_CONSUMER_KEY = os.getenv("TWITTER_AUTH_CONSUMER_KEY")
TWITTER_AUTH_CONSUMER_SECRET = os.getenv("TWITTER_AUTH_CONSUMER_SECRET")
TWITTER_AUTH_BEARER_TOKEN = os.getenv("TWITTER_AUTH_BEARER_TOKEN")
TWITTER_AUTH_ACCESS_TOKEN = os.getenv("TWITTER_AUTH_ACCESS_TOKEN")
TWITTER_AUTH_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_AUTH_ACCESS_TOKEN_SECRET")

# openai api
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CLIENT_ID = os.getenv("CLIENT_ID")
OPENAI_CLIENT_SECRET = os.getenv("CLIENT_SECRET")

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
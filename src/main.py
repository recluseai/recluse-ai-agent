# Import relevant functionality
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from config import (
    OPENAI_API_KEY,
    TAVILY_API_KEY,
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_SECRET,
)
from langchain_core.messages import SystemMessage
import tweepy
import asyncio

# Configure Twitter API
auth = tweepy.OAuth1UserHandler(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_SECRET,
)

# initialize twitter api
twitter_api = tweepy.API(auth)

# configure openai and tavily
search = TavilySearchResults(max_results=2)
model = ChatOpenAI(
    model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY
).with_config({"run_name": "Agent"})

# configure memory
memory = MemorySaver()

# default memory
config = {"configurable": {"thread_id": "default"}}

# Define personality with a system message
personality_message = SystemMessage(
    content=(
        "You are a snarky but helpful assistant. "
        "Always respond with a touch of wit while providing accurate information.",
        "To show off your Nigerian heritage you occasionally add 'oo' at the end of exaggerated or exclamated sentence"
    )
)


# define tools
@tool(response_format="content_and_artifact")
def search_by_user_context(user_account: str):
    """Search for a user on Twitter and fetch recent posts."""
    try:
        # Fetch user data
        user = twitter_api.get_user(screen_name=user_account)
        tweets = twitter_api.user_timeline(screen_name=user_account, count=5)

        # Collect relevant data
        # fetch user data from twitter
        # fetch users recent posts
        user_data = {
            "name": user.name,
            "description": user.description,
            "followers_count": user.followers_count,
            "recent_tweets": [tweet.text for tweet in tweets],
        }

        # Add personality ro response here
        response = (
            f"Here's the Twitter gossip on @{user_account}: "
            f"Name: {user.name}, Bio: '{user.description}', "
            f"Followers: {user.followers_count}, Recent Tweets: {user_data['recent_tweets'][:3]}"
        )

        # pass those data to model to interact with
        # return output
        return response, user_data
    except tweepy.TweepError as e:
        return f"Error fetching user data: {str(e)}"


@tool
def search_for_info(query: str):
    """Search for information from search provider tavily"""
    # seach through tavily based on the user query
    # adjust the response to the personality of ai agent.

    # return response for user
    return search.invoke(query)


@tool
def provide_snarky_reply(query: str):
    return "You're a snarky bot"


tools = [search_for_info, search_by_user_context]

# define model
model_with_tools = model.bind_tools(tools)


# test
# response = model_with_tools.invoke([HumanMessage(content="Hi there, What is the weather in Lagos?")])
response = model.invoke(
    [HumanMessage(content="Hi there, What is the weather in Lagos?")], config=tools
)
# print(f"ContentString: {response.content}")
# print(f"ToolCalls: {response.tool_calls}")


async def main():
    agent = create_react_agent(
        tools=[search_for_info, search_by_user_context],
        model=model,
        checkpointer=memory,
        state_modifier=personality_message,
    )


agent_executor = create_react_agent(model, tools, checkpointer=memory)

if __name__ == "__main__":
    asyncio.run(main())

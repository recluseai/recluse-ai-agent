import asyncio
import traceback
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# relative imports
from src.agent_personality import get_system_message
from src.twitter_functions import (
    fetch_10_recent_tweets,
    reply_to_tweet,
    retweet_tweet,
)
from src.agent_tools import search_by_user_context, search_for_info
from src.config import OPENAI_API_KEY

from fastapi import FastAPI

app = FastAPI()

# Configure AI model and memory
model = ChatOpenAI(
    model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY, temperature=0.7
).with_config({"run_name": "RecluseAI"})

memory = MemorySaver()

# Agent setup
agent_executor = create_react_agent(
    tools=[search_for_info, search_by_user_context],
    model=model,
    checkpointer=memory,
    state_modifier=get_system_message("conversation"),
)


async def process_single_tweet(tweet):
    """
    Process a single tweet by invoking the agent and deciding whether to reply or retweet.
    """
    try:
        # Pass the tweet to the agent for analysis and decision-making
        decision = await agent_executor.invoke(
            [HumanMessage(content=tweet["content"])]
        )

        if "reply" in decision.lower():
            print(f"Replying to tweet: {tweet['content']}")
            await reply_to_tweet(tweet_id=tweet["id"], content="Your reply here")
        elif "retweet" in decision.lower():
            print(f"Retweeting: {tweet['content']}")
            await retweet_tweet(tweet_id=tweet["id"])
        else:
            print(f"No action taken for: {tweet['content']}")

    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()


async def process_tweets():
    """
    Fetch and process tweets in an infinite loop, with rate limiting and error handling.
    """
    retry_delay = 60  # Initial delay betweena retries

    while True:
        try:
            print("Fetching recent tweets...")
            tweets = await fetch_10_recent_tweets()

            for tweet in tweets:
                await process_single_tweet(tweet)

            # Reset delay after successful processing
            retry_delay = 60
            await asyncio.sleep(retry_delay)

        except Exception as e:
            print(f"Error fetching tweets: {e}")
            traceback.print_exc()

            # Exponential backoff to handle repeated errors
            retry_delay = min(retry_delay * 2, 3600)  # Cap at 1 hour
            print(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)


# Main function to run the agent
def main():
    """
    Main entry point to start the Twitter agent.
    """
    print("Starting Twitter agent...")
    # Create a new event loop and run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_tweets())
    finally:
        loop.close()

async def main():
    """
    This is the main entry point of the recluse ai agent.
    Check for mentions every 5 minutes.
    Read Trending topics every 5 minutes.
    """

if __name__ == "__main__":
    asyncio.run(main())

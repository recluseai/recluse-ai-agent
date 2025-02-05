import asyncio
import traceback
from redis.asyncio import Redis

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# Relative imports
from src.agent_personality import get_system_message
from src.twitter_functions import (
    fetch_10_recent_tweets,
    reply_to_tweet,
    retweet_tweet,
    read_mentions,
)
from src.agent_tools import search_by_user_context, search_for_info
from src.config import OPENAI_API_KEY


# global declaration of redis
redis = None


async def init_redis():
    """Initialize Redis connection."""
    global redis
    redis = await Redis.from_url("redis://localhost", decode_responses=True)
    print("Redis connected!")


async def close_redis():
    """Close Redis connection properly."""
    global redis
    if redis:
        await redis.close()
        print("Redis connection closed!")


# Configure AI model and memory
model = ChatOpenAI(
    model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY, temperature=0.7
).with_config({"run_name": "RecluseAI"})

memory = MemorySaver()
thread_id = "test_thread"
config = {"configurable": {"thread_id": thread_id}}
# Agent setup
agent_executor = create_react_agent(
    tools=[search_for_info, search_by_user_context],
    model=model,
    checkpointer=memory,
    state_modifier=get_system_message("conversation"),
)


async def decide_task():
    """
    Let GPT decide whether to process mentions, fetch tweets, or do nothing.
    """
    prompt = """
    Given the current situation of the Twitter AI agent, decide the best action to take.
    
    Options:
    - mentions → If the AI was mentioned recently and needs to respond.
    - tweets → If the AI should fetch and process recent tweets.
    - none → If no action is needed.
    
    Analyze and return either mentions or tweets, none option string, without the quotations.
    """

    response = model.invoke([HumanMessage(content=prompt)])
    decision = response.content.strip().lower()
    print("Decision: ", decision)
    return decision


async def identify_bot(tweet):
    """
    Identify if a tweet is from a bot."""
    try:
        prompt = """
        do not reply, like or retweet to accounts you are suspicious of being a bot. or propagating uninterested content. just output none."""
        print("tweet to be processed: ", tweet)
        decision = agent_executor.invoke(
            {"messages": [HumanMessage(content=f"{prompt}\n\n{tweet}")]}, config=config
        )

        decision_return_value = decision["messages"][1].content
        return decision_return_value.lower()
    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()


async def process_single_tweet(tweet):
    """
    Process a single tweet by invoking the agent and deciding whether to reply or retweet.
    """
    try:
        decision = await identify_bot(tweet)

        prompt = """
        reply to this tweet
        """

        decision = agent_executor.invoke(
            {"messages": [HumanMessage(content=f"{prompt}\n\n{tweet}")]}, config=config
        )

        # decision_return_value = decision["messages"][0].content
        print("Decision: ", decision)
        decision_return_value = decision["messages"][1].content
        print("Decision return value: ", decision_return_value)

        # if "reply" in decision.lower():
        #     print(f"Replying to tweet: {tweet['id']}")
        #     await reply_to_tweet(tweet_id=tweet["id"], content="Your reply here")
        # elif "retweet" in decision.lower():
        #     print(f"Retweeting: {tweet['id']}")
        #     await retweet_tweet(tweet_id=tweet["id"])
        # else:
        #     print(f"No action taken for: {tweet['id']}")

    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()


async def process_mentions():
    """
    Fetch and respond to  Twitter mentions.
    """
    try:
        print("Checking mentions...")
        mentions = await read_mentions("recluseai_", redis)
        # print("mentions: ", mentions)

        # if mentions["mentions_tweet"]:  # Ensure there's at least one tweet
        #     first_tweet = mentions["mentions_tweet"][0]
        #     await process_single_tweet(first_tweet["original_tweet"])

        for tweet in mentions["mentions_tweet"]:
            print(type(tweet["original_tweet"]))
            print('this is the original tweet to be processed: ', tweet["original_tweet"])
            # await process_single_tweet(tweet["original_tweet"])

    except Exception as e:
        print(f"Error processing mentions: {e}")
        traceback.print_exc()


async def process_tweets():
    """
    Fetch and process recent tweets.
    """
    try:
        print("Fetching recent tweets...")
        tweets = await fetch_10_recent_tweets()
        print("list of tweets fetched: ", tweets)
        for tweet in tweets:
            print("tweet passed: ", tweet)
            await process_single_tweet(tweet)

    except Exception as e:
        print(f"Error fetching tweets: {e}")
        traceback.print_exc()


async def main():
    """
    Main loop: Start ai agent by deciding which task to execute and run accordingly.
    """
    print("Starting RecluseAI Twitter agent...")

    await init_redis()

    try:
        while True:
            await process_mentions()
            await asyncio.sleep(60)

            # task = await decide_task()
            # print("Task: ", task)

            # if task == "mentions":
            #     await process_mentions()
            # elif task == "tweets":
            #     await process_tweets()
            # else:
            #     print("No action needed. Sleeping for 1/2 minute.")
            await asyncio.sleep(30)  # Wait 5 minutes before checking again
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
    finally:
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())

# Steps to ai agent

# start ai agent --- [done]
# ai agent decides what to do --- [skip for now]
## if decision is 'check mentions'
# read recent mentions --- [done]
# ai agent decides whether mention is bot or real.
# for bots, ignore.
# for real users, ai agent interprets the type of request.
# if request is for information, ai agent searches for information.
# if request is for a reply, ai agent comes up with a reply.
# if request is for retweet, ai agent retweets the tweet.


# types of request
## if decision is tweets, run process tweets
## if decision is none | 'caught up', sleep for 1/2 minute

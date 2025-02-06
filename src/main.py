import asyncio
import traceback
from redis.asyncio import Redis

# langchain imports
from langchain_core.messages import HumanMessage, SystemMessage

# Relative imports
from src.config import agent_executor, config
from src.twitter_functions import (
    search_for_tweets,
    fetch_10_recent_tweets,
    reply_to_tweet,
    retweet_tweet,
    read_mentions,
)
from src.utils.agent_helpers import provide_conversation_context

# from src.agent_tools import search_by_user_context, search_for_info
# from src.config import OPENAI_API_KEY


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


async def identify_bot(tweet):
    """
    Identify if a tweet is from a bot."""
    try:
        prompt = """
        identify if account is suspicious of being a bot.
        if account is a bot, output 'suspicious' without the quotations.
        if account is not a bot, output 'proceed' without the quotations.
        """

        print("tweet to be processed: ", tweet)
        decision = agent_executor.invoke(
            {"messages": [HumanMessage(content=f"{prompt}\n\n{tweet}")]}, config=config
        )
        decision_return_value = decision["messages"][1].content

        # print("decision return value: ", decision_return_value)

        if decision_return_value.lower() == "suspicous":
            return True
        else:
            return False

    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()


async def process_single_mention(tweet, tweet_id):
    """
    Process a single tweet by invoking the agent and deciding whether to reply or retweet.
    """

    try:
        is_bot = await identify_bot(tweet)
        print("is bot: ", is_bot)
        is_bot = False

        prompt = """
        reply to this tweet
        """

        print(f"{prompt}\n\n{tweet}")

        if not is_bot:
            conversation_context = await provide_conversation_context(tweet)
            print("this is what conversation context decided: ", conversation_context)

            if conversation_context.lower().strip() == "conversation":
                response = agent_executor.invoke(
                    {
                        "messages": [
                            SystemMessage(content="Respond only to the given input."),
                            HumanMessage(content=f"{prompt}\n\n{tweet}"),
                        ]
                    },
                    config={**config, "memory": None},
                )
                decision_return_value = response["messages"][-1].content
                print("Query reply from return value: ", decision_return_value)

                # reply to tweet
                await reply_to_tweet(
                    tweet_id=tweet_id, message=decision_return_value, redis=redis
                )
            elif conversation_context.lower().strip() == "query":
                response = await search_for_tweets(redis, keyword=tweet, count=70)
                print("conversation reply from single tweet: ", response['response'])
                print('tweet id: ', tweet_id)
                tweet_reply = response["response"]

                # reply to tweet
                await reply_to_tweet(
                    tweet_id=tweet_id, message=tweet_reply, redis=redis
                )

    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()


async def process_mentions():
    """
    Fetch and respond to Twitter mentions.
    """
    try:
        print("Checking mentions...")
        mentions = await read_mentions("recluseai_", redis)

        for tweet in mentions["mentions_tweet"]:
            # print('this is the original tweet to be processed: ', tweet["original_tweet"])
            await process_single_mention(tweet["original_tweet"], tweet_id=tweet["id"])

    except Exception as e:
        print(f"Error processing mentions: {e}")
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

            await asyncio.sleep(90)  # Wait for 1.5 minutes before checking again
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

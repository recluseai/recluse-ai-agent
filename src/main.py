import asyncio
import traceback
from redis.asyncio import Redis

# Relative imports
from src.config import agent_executor, config, supabase, redis_url, call_openai, call_openai_with_throttling
from src.twitter_functions import (
    search_for_tweets,
    fetch_10_recent_tweets,
    reply_to_tweet,
    retweet_tweet,
    read_mentions,
)
from src.utils.agent_helpers import provide_conversation_context, respond_to_conversation

# Global Redis declaration
redis = None


async def init_redis():
    """Initialize Redis connection."""
    global redis
    redis = await Redis.from_url(
        redis_url, decode_responses=True    
    )
    print("Redis connected!")


async def close_redis():
    """Close Redis connection properly."""
    global redis
    if redis:
        await redis.close()
        print("Redis connection closed!")


async def identify_bot(tweet):
    """Identify if a tweet is from a bot."""
    try:
        prompt = """
        Identify if the account is suspicious of being a bot.
        If account is asking you a question, they are most likely not a bot. So proceed.
        If the account is a bot, output 'suspicious' without the quotations.
        If the account is not a bot, output 'proceed' without the quotations.
        """

        print("Processing tweet for bot detection:", tweet)
        decision = call_openai_with_throttling(f"{prompt}\n\n{tweet}")
        decision_return_value = decision["messages"][-1].content

        if (
            decision_return_value
            and decision_return_value.strip().lower() == "suspicious"
        ):
            return True
        return False

    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()
        return False


async def process_single_mention(tweet, tweet_id):
    """Process a single tweet by invoking the agent and deciding whether to reply or retweet."""
    try:
        is_bot = await identify_bot(tweet)
        print("Bot detection result:", is_bot)
        
        if is_bot:
            supabase.table("recluse_mentions").update({"bot_status": True}).eq("id", tweet_id).execute()

        if not is_bot:
            conversation_context = await provide_conversation_context(tweet)
            print("Conversation context result:", conversation_context)

            if conversation_context.lower().strip() == "conversation":
                response = respond_to_conversation(tweet)
                print("AI response conversation:", response)

                if response:
                    await reply_to_tweet(
                        tweet_id=tweet_id, message=response, redis=redis
                    )
                    
                    supabase.table("recluse_mentions").update(
                        {"replied_status": True}
                    ).eq("id", tweet_id).execute()
                    print("Tweet replied to and database updated.")

            elif conversation_context.lower().strip() == "twitter":
                response = await search_for_tweets(redis, keyword=tweet, count=40)
                tweet_reply = response.get("response", "No relevant results found.")

                await reply_to_tweet(
                    tweet_id=tweet_id, message=tweet_reply, redis=redis
                )
                supabase.table("recluse_mentions").update({"replied_status": True}).eq(
                    "id", tweet_id
                ).execute()
                print("Query-based tweet reply sent.")

    except Exception as e:
        print(f"Error processing tweet: {e}")
        traceback.print_exc()


async def process_mentions():
    """Fetch and respond to Twitter mentions."""
    try:
        print("Checking mentions...")
        mentions = await read_mentions("recluseai_", redis)

        for tweet in mentions["mentions_tweet"]:
            tweet_id = tweet["id"]

            response = (
                supabase.table("recluse_mentions")
                .select("*")
                .eq("id", tweet_id)
                .execute()
            )

            if response.data:
                is_bot =  response.data[0].get("bot_status")
                is_replied = response.data[0].get("replied_status")
                
                # Check if tweet is a bot
                if is_bot:
                    # print("is bot: ", is_bot)
                    print(f"Tweet {tweet_id} is from a bot. Skipping...")
                    continue
                
                # Check if the tweet has been replied to
                if is_replied:
                    print(f"Tweet {tweet_id} has already been replied to. Skipping...")
                    continue

            else:
                supabase.table("recluse_mentions").insert(
                    {"id": tweet_id, "replied_status": False}
                ).execute()
            await process_single_mention(tweet["original_tweet"], tweet_id=tweet_id)

    except Exception as e:
        print(f"Error processing mentions: {e}")
        traceback.print_exc()


async def main():
    """Main loop: Start AI agent and process mentions in a loop."""
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
# ai agent decides whether mention is bot or real. [done]
# for bots, ignore. [done]
# for real users, ai agent interprets the type of request. [done]
# if request is for information, ai agent searches for information. [done]
# if request is for a reply, ai agent comes up with a reply. [done]
# if request is for retweet, ai agent retweets the tweet. [pending]


# types of request
## if decision is tweets, run process tweets
## if decision is none | 'caught up', sleep for 1/2 minute

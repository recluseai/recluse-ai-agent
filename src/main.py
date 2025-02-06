import time
import openai
import asyncio
import traceback
from redis.asyncio import Redis
from tenacity import retry, stop_after_attempt, wait_exponential

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage

# Relative imports
from src.config import agent_executor, config, supabase
from src.twitter_functions import (
    search_for_tweets,
    fetch_10_recent_tweets,
    reply_to_tweet,
    retweet_tweet,
    read_mentions,
)
from src.utils.agent_helpers import provide_conversation_context

# Global Redis declaration
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

# Initialize rate limiting variables
REQUEST_INTERVAL = 5  # 5 seconds between requests
last_request_time = time.time()

# Exponential backoff for OpenAI API calls
@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
def call_openai(prompt):
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={**config, "stream": True}  # Enable streaming for efficiency
    )
    return response

def call_openai_with_throttling(prompt):
    global last_request_time, REQUEST_INTERVAL

    # Ensure a gap between API calls
    time_since_last_request = time.time() - last_request_time
    if time_since_last_request < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - time_since_last_request)

    last_request_time = time.time()

    try:
        return call_openai(prompt)  # Call OpenAI with retry logic
    except openai.error.RateLimitError:
        print("⚠️ Rate limit hit! Increasing interval to prevent further 429 errors.")
        REQUEST_INTERVAL += 2  # Increase delay dynamically
        return None

async def identify_bot(tweet):
    """Identify if a tweet is from a bot."""
    try:
        prompt = """
        Identify if the account is suspicious of being a bot.
        If the account is a bot, output 'suspicious' without the quotations.
        If the account is not a bot, output 'proceed' without the quotations.
        """
        
        print("Processing tweet for bot detection:", tweet)
        decision = call_openai_with_throttling(f"{prompt}\n\n{tweet}")
        decision_return_value = decision["messages"][-1].content

        if decision_return_value and decision_return_value.strip().lower() == "suspicious":
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
        
        if not is_bot:
            conversation_context = await provide_conversation_context(tweet)
            print("Conversation context result:", conversation_context)
            
            if conversation_context.lower().strip() == "conversation":
                response = call_openai_with_throttling(tweet)
                print("AI response:", response)

                if response:
                    await reply_to_tweet(tweet_id=tweet_id, message=response, redis=redis)
                    supabase.table("recluse_mentions").update({"replied_status": True}).eq("id", tweet_id).execute()
                    print("Tweet replied to and database updated.")
                
            elif conversation_context.lower().strip() == "query":
                response = await search_for_tweets(redis, keyword=tweet, count=50)
                tweet_reply = response.get("response", "No relevant results found.")
                
                await reply_to_tweet(tweet_id=tweet_id, message=tweet_reply, redis=redis)
                supabase.table("recluse_mentions").update({"replied_status": True}).eq("id", tweet_id).execute()
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

            # Check if the tweet has been replied to
            response = supabase.table("recluse_mentions").select("replied_status").eq("id", tweet_id).execute()
            
            if response.data: 
                if response.data[0].get("replied_status"):
                    print(f"Tweet {tweet_id} has already been replied to. Skipping...")
                    continue
            
            else: 
                supabase.table("recluse_mentions").insert({"id": tweet_id, "replied_status": False}).execute()
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

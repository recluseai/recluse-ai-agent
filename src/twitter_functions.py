from fastapi import FastAPI, HTTPException, Query
from .config import (
    TWITTER_AUTH_CONSUMER_KEY,
    TWITTER_AUTH_CONSUMER_SECRET,
    TWITTER_AUTH_ACCESS_TOKEN,
    TWITTER_AUTH_ACCESS_TOKEN_SECRET,
    TWITTER_AUTH_BEARER_TOKEN,
)
from tweepy import Client
from typing import Union
from aiolimiter import AsyncLimiter

import datetime
import logging
import time
import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# predefined classes
class ReplyRequest(BaseModel):
    tweet_id: int
    message: str


class TweetContent(BaseModel):
    content: str


# Instantiate FastAPI app
app = FastAPI()

# Configure Tweepy client
client = Client(
    bearer_token=TWITTER_AUTH_BEARER_TOKEN,
    access_token=TWITTER_AUTH_ACCESS_TOKEN,
    access_token_secret=TWITTER_AUTH_ACCESS_TOKEN_SECRET,
    consumer_key=TWITTER_AUTH_CONSUMER_KEY,
    consumer_secret=TWITTER_AUTH_CONSUMER_SECRET,
)


# Rate limiter callback
def rate_limit_callback(until):
    duration = int(round(until - time.time()))
    logger.warning(f"Rate limited. Sleeping for {duration} seconds.")


# rate_limiter = RateLimiter(max_calls=15, period=60 * 15, callback=rate_limit_callback)
# rate_limiter_fetch_tweets = RateLimiter(max_calls=15, period=60 * 15, callback=rate_limit_callback)

rate_limiter = AsyncLimiter(max_rate=15, time_period=60 * 15)
limiter_fetch_tweets = AsyncLimiter(max_rate=15, time_period=60 * 15)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter AI Agent!"}


# twitter mentions function
@app.post("/mentions/{username}")
async def read_mentions(username: str):
    """
    Fetches the latest mentions for RecluseAI.
    """
    try:
        async with rate_limiter:
            today = datetime.time()
            print(f"Today's date and time: {today}")
            print(f"This is the user username: {username}")
            user = client.get_user(username=username)
            print(f"This is the user id: {user.data["id"]}")
            mentions = client.get_users_mentions(id=user.data["id"])
            print(f"This is the user mentions: {mentions}")
            tweets = [{"id": mention.id, "text": mention.text, "user": mention.user.screen_name} for mention in mentions]
            return {"status": "success", "mentions": tweets}
    except Exception as e:
        logger.error(f"Error fetching mentions: {e}")
        raise HTTPException(status_code=500, detail="Error fetching mentions")
    
# twitter tweet functions

@app.post("/tweet")
def post_tweet(content: str):
    """
    Posts a new tweet.
    """
    try:
        with rate_limiter:
            tweet = client.create_tweet(text=content)
        return {
            "status": "success",
            "tweet_id": tweet.data["id"],
            "content": tweet.data["text"],
        }
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        raise HTTPException(status_code=500, detail="Error posting tweet")

@app.post("/retweet")
async def retweet_tweet(tweet_id: int):
    """
    Retweets a specified tweet.
    """
    try:
        async with rate_limiter:
            response = client.retweet(tweet_id=tweet_id)

        return {
            "status": "success",
            "tweet_id": tweet_id,
            "message": "Tweet retweeted successfully!",
        }
    except Exception as e:
        logger.error(f"Error retweeting tweet: {e}")
        raise HTTPException(status_code=500, detail="Error retweeting tweet")

@app.post("/reply_to_tweet")
def reply_to_tweet(request: ReplyRequest):
    """
    Replies to a tweet with the given message.
    """
    try:
        tweet_id = request.tweet_id
        message = request.message

        if len(message) > 280:
            raise ValueError(
                "Message exceeds Twitter's character limit (280 characters)."
            )
        # call openai function to regenerate tweet if context window exceeds 280 characters
        with rate_limiter:
            # Simulated API call for reply
            response = client.create_tweet(text=message, in_reply_to_tweet_id=tweet_id)

        logger.info(f"Reply sent successfully to tweet ID {tweet_id}: {message}")
        return {
            "status": "success",
            "reply_id": response["id"],
            "message": "Reply sent successfully!",
        }

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"Error replying to tweet: {e}")
        raise HTTPException(status_code=500, detail="Error replying to tweet")

@app.get("/fetch_10_recent_tweets")
async def fetch_10_recent_tweets(count: int = 10):
    """
    Fetches the latest tweets from the authenticated user's timeline.
    """
    try:
        async with limiter_fetch_tweets:
            response = client.get_home_timeline(max_results=count)
            if response.data:
                tweets = [
                    {"id": tweet.id, "text": tweet.text} for tweet in response.data
                ]
            else:
                tweets = []
        return {"data": tweets, "count": len(tweets)}
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tweets")

@app.get("/fetch_tweets")
async def fetch_tweets(count: int = 10, search: str = Query(default=None)):
    """
    Fetches the latest tweets from the authenticated user's timeline.
    Optionally filters tweets by a search query.
    """
    try:
        async with limiter_fetch_tweets:
            # Fetch tweets from the timeline
            response = client.get_home_timeline(max_results=count)

            if not response.data:
                return {"data": [], "count": 0}

            # Extract tweets
            tweets = [{"id": tweet.id, "text": tweet.text} for tweet in response.data]

            # Apply search filter if a query is provided
            if search:
                search = search.lower()
                tweets = [
                    tweet for tweet in tweets if search in tweet["text"].lower()
                ]

        return {"data": tweets, "count": len(tweets)}
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tweets")

#twitter user functions
@app.get("/find_user")
async def find_user(username: str = None, user_id: int = None):
    """
    Finds a user by their username or user ID.
    """
    try:
        if not username and not user_id:
            raise HTTPException(status_code=400, detail="Provide either a username or user_id.")
        
        async with rate_limiter:
            if username:
                user = client.get_user(username=username)
            elif user_id:
                user = client.get_user(user_id=user_id)
        
        return {
            "status": "success",
            "data": {
                "id": user.data["id"],
                "name": user.data["name"],
                "username": user.data["username"],
                "description": user.data.get("description", ""),
                "followers": user.data.get("public_metrics", {}).get("followers_count", 0),
            },
        }
    except Exception as e:
        logger.error(f"Error finding user: {e}")
        raise HTTPException(status_code=500, detail="Error finding user")

# @app.get("/analyze_user")
# async def analyze_user(username: str):
#     """
#     Analyzes a user's profile information for insights or sentiment.
#     """
#     try:
#         async with rate_limiter:
#             user = client.get_user(username=username)
        
#         bio = user.data.get("description", "")
#         followers = user.data.get("public_metrics", {}).get("followers_count", 0)

#         # Simple analysis
#         sentiment = "positive" if "love" in bio.lower() else "neutral"
#         popularity = "influencer" if followers > 10000 else "average user"

#         return {
#             "status": "success",
#             "analysis": {
#                 "bio_sentiment": sentiment,
#                 "popularity": popularity,
#                 "bio": bio,
#                 "followers": followers,
#             },
#         }
#     except Exception as e:
#         logger.error(f"Error analyzing user: {e}")
#         raise HTTPException(status_code=500, detail="Error analyzing user")

@app.get("/latest_tweets")
async def scan_latest_tweets(username: str, count: int = 5):
    """
    Scans a user's latest tweets.
    """
    try:
        async with rate_limiter:
            user = client.get_user(username=username)
            user_id = user.data["id"]
            tweets = client.get_users_tweets(id=user_id, max_results=count)

        tweet_data = [{"id": tweet.id, "text": tweet.text} for tweet in tweets.data]

        return {"status": "success", "tweets": tweet_data}
    except Exception as e:
        logger.error(f"Error fetching latest tweets: {e}")
        raise HTTPException(status_code=500, detail="Error fetching latest tweets")

@app.get("/relevant_tweets")
async def scan_relevant_tweets(username: str, keyword: str, count: int = 5):
    """
    Scans a user's tweets for relevance based on a keyword.
    """
    try:
        async with rate_limiter:
            user = client.get_user(username=username)
            user_id = user.data["id"]
            tweets = client.get_users_tweets(id=user_id, max_results=100)

        # Filter tweets based on the keyword
        relevant_tweets = [
            {"id": tweet.id, "text": tweet.text}
            for tweet in tweets.data
            if keyword.lower() in tweet.text.lower()
        ][:count]

        return {"status": "success", "relevant_tweets": relevant_tweets}
    except Exception as e:
        logger.error(f"Error fetching relevant tweets: {e}")
        raise HTTPException(status_code=500, detail="Error fetching relevant tweets")

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/analyze")
def analyze_crypto_sentiment(tweet_text: str):
    prompt = f"""
    Analyze the sentiment of the following tweet specifically in the context of cryptocurrency. 
    Classify the sentiment as one of the following:
    - 'bullish' if the tweet shows optimism, excitement, or positive expectations about cryptocurrency prices or trends.
    - 'bearish' if the tweet expresses pessimism, concerns, or negative expectations about cryptocurrency prices or trends.
    - 'neutral' if the tweet does not clearly express bullish or bearish sentiment.

    Provide the classification and a brief explanation of your reasoning.

    Tweet: "{tweet_text}"
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )
    result = response["choices"][0]["message"]["content"].strip()
    return result

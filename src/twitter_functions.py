from fastapi import FastAPI, HTTPException
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

import logging
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

rate_limiter = AsyncLimiter(max_rate=15, time_period=60*15);
limiter_fetch_tweets = AsyncLimiter(max_rate=15, time_period=60*15);

@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter AI Agent!"}


@app.get("/tweets")
async def fetch_tweets(count: int = 10):
    """
    Fetches the latest tweets from the authenticated user's timeline.
    """
    try:
        async with limiter_fetch_tweets:
            response = client.get_home_timeline(max_results=count)
            if response.data:
                tweets = [{"id": tweet.id, "text": tweet.text} for tweet in response.data]
            else:
                tweets = []
        return {"data": tweets, "count": len(tweets)}
    except Exception as e:
        logger.error(f"Error fetching tweets: {e}")
        raise HTTPException(status_code=500, detail="Error fetching tweets")


@app.post("/analyze")
def analyze_tweet(tweet_id: int):
    """
    Analyzes a specific tweet for sentiment or keywords.
    """
    try:
        with rate_limiter:
            tweet = client.get_tweet(tweet_id)
        # Placeholder for AI analysis
        sentiment = "positive" if "good" in tweet.data["text"].lower() else "neutral"
        return {"id": tweet.data["id"], "text": tweet.data["text"], "sentiment": sentiment}
    except Exception as e:
        logger.error(f"Error analyzing tweet: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing tweet")


@app.post("/reply")
def reply_to_tweet(tweet_id: int, message: str):
    """
    Replies to a tweet with the given message.
    """
    try:
        with rate_limiter:
            client.create_tweet(text=message, in_reply_to_tweet_id=tweet_id)
        return {"status": "success", "message": "Reply sent!"}
    except Exception as e:
        logger.error(f"Error replying to tweet: {e}")
        raise HTTPException(status_code=500, detail="Error replying to tweet")


@app.post("/post")
def post_tweet(content: str):
    """
    Posts a new tweet.
    """
    try:
        with rate_limiter:
            tweet = client.create_tweet(text=content)
        return {"status": "success", "tweet_id": tweet.data["id"], "content": tweet.data["text"]}
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        raise HTTPException(status_code=500, detail="Error posting tweet")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

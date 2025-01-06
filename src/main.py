from typing import Union
from fastapi import FastAPI
from config import ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY,CONSUMER_SECRET
import tweepy

app = FastAPI()

auth = tweepy.OAuth1UserHandler(
    CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)

client = tweepy.Client(auth)

public_tweets = client.get_home_timeline()
for tweet in public_tweets.data:
    print(tweet.text)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Twitter AI Agent!"}

@app.get("/tweets")
def fetch_tweets(count: int = 10):
    """
    Fetches the latest tweets from the authenticated user's timeline.
    :param count: Number of tweets to fetch.
    """
    try:
        public_tweets = client.home_timeline(count=count)
        tweets = [{"id": tweet.id, "text": tweet.text} for tweet in public_tweets]
        return {"tweets": tweets}
    except Exception as e:
        return {"error": str(e)}


@app.post("/analyze")
def analyze_tweet(tweet_id: int):
    """
    Analyzes a specific tweet for sentiment or keywords.
    :param tweet_id: ID of the tweet to analyze.
    """
    try:
        tweet = client.get_status(tweet_id)
        # Placeholder for AI analysis
        sentiment = "positive" if "good" in tweet.text.lower() else "neutral"
        return {"id": tweet.id, "text": tweet.text, "sentiment": sentiment}
    except Exception as e:
        return {"error": str(e)}


@app.post("/reply")
def reply_to_tweet(tweet_id: int, message: str):
    """
    Replies to a tweet with the given message.
    :param tweet_id: ID of the tweet to reply to.
    :param message: Reply message content.
    """
    try:
        client.update_status(status=message, in_reply_to_status_id=tweet_id)
        return {"status": "success", "message": "Reply sent!"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/post")
def post_tweet(content: str):
    """
    Posts a new tweet.
    :param content: Content of the tweet.
    """
    try:
        tweet = client.update_status(content)
        return {"status": "success", "tweet_id": tweet.id, "content": tweet.text}
    except Exception as e:
        return {"error": str(e)}

#tests
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
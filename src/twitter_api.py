# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Union
# import tweepy

# # Configuration variables (ensure these are securely stored, e.g., in environment variables)
# from config import (
#     TWITTER_OAUTH_CONSUMER_KEY,
#     TWITTER_OAUTH_CONSUMER_SECRET,
#     TWITTER_AUTH_ACCESS_TOKEN,
#     TWITTER_AUTH_ACCESS_TOKEN_SECRET,
# )

# # FastAPI app initialization
# app = FastAPI()

# # Tweepy authentication
# auth = tweepy.OAuth1UserHandler(
#     TWITTER_OAUTH_CONSUMER_KEY,
#     TWITTER_OAUTH_CONSUMER_SECRET,
#     TWITTER_AUTH_ACCESS_TOKEN,
#     TWITTER_AUTH_ACCESS_TOKEN_SECRET,
# )
# client = tweepy.API(auth)


# ### Models
# class TweetContent(BaseModel):
#     content: str


# class ReplyContent(BaseModel):
#     tweet_id: int
#     message: str


# class SearchQuery(BaseModel):
#     query: str
#     count: int = 10  # Default to fetching 10 results


# ### Endpoints

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Twitter AI Agent!"}


# @app.post("/post")
# def post_tweet(tweet: TweetContent):
#     """
#     Posts a new tweet.
#     """
#     try:
#         posted_tweet = client.update_status(tweet.content)
#         return {"status": "success", "tweet_id": posted_tweet.id, "content": posted_tweet.text}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post("/reply")
# def reply_to_tweet(reply: ReplyContent):
#     """
#     Replies to a tweet with the given message.
#     """
#     try:
#         replied_tweet = client.update_status(
#             status=reply.message,
#             in_reply_to_status_id=reply.tweet_id,
#             auto_populate_reply_metadata=True,
#         )
#         return {"status": "success", "reply_id": replied_tweet.id, "message": reply.message}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.get("/profile/{username}")
# def get_user_profile(username: str):
#     """
#     Fetches user profile information by username.
#     """
#     try:
#         user = client.get_user(screen_name=username)
#         profile = {
#             "id": user.id,
#             "name": user.name,
#             "username": user.screen_name,
#             "description": user.description,
#             "followers_count": user.followers_count,
#             "following_count": user.friends_count,
#             "profile_image_url": user.profile_image_url_https,
#         }
#         return {"status": "success", "profile": profile}
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))


# @app.get("/mentions")
# def get_mentions(count: int = 10):
#     """
#     Fetches the latest mentions of the authenticated user.
#     """
#     try:
#         mentions = client.mentions_timeline(count=count)
#         tweets = [{"id": mention.id, "text": mention.text, "user": mention.user.screen_name} for mention in mentions]
#         return {"status": "success", "mentions": tweets}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.get("/trending/{woeid}")
# def get_trending_tags(woeid: int):
#     """
#     Fetches trending hashtags for a given location (WOEID - Where On Earth IDentifier).
#     """
#     try:
#         trends = client.get_place_trends(id=woeid)
#         trending = [{"name": trend["name"], "tweet_volume": trend["tweet_volume"]} for trend in trends[0]["trends"]]
#         return {"status": "success", "trending": trending}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post("/search")
# def search_tweets(search_query: SearchQuery):
#     """
#     Searches for tweets based on a query string.
#     """
#     try:
#         tweets = client.search_tweets(q=search_query.query, count=search_query.count, result_type="recent")
#         results = [{"id": tweet.id, "text": tweet.text, "user": tweet.user.screen_name} for tweet in tweets]
#         return {"status": "success", "tweets": results}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.get("/timeline")
# def get_home_timeline(count: int = 10):
#     """
#     Fetches the authenticated user's home timeline.
#     """
#     try:
#         public_tweets = client.home_timeline(count=count)
#         tweets = [{"id": tweet.id, "text": tweet.text, "user": tweet.user.screen_name} for tweet in public_tweets]
#         return {"status": "success", "tweets": tweets}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# ### Additional Considerations
# # - Add rate limiting to handle Twitter API rate limits gracefully.
# # - Include logging for better debugging and monitoring.


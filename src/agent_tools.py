from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from .config import (
    OPENAI_API_KEY,
    TAVILY_API_KEY,
    TWITTER_AUTH_CONSUMER_KEY,
    TWITTER_AUTH_CONSUMER_SECRET,
    TWITTER_AUTH_ACCESS_TOKEN,
    TWITTER_AUTH_ACCESS_TOKEN_SECRET,
    TWITTER_AUTH_BEARER_TOKEN,
)
import tweepy

# Configure Twitter API
auth = tweepy.OAuth1UserHandler(
    consumer_key=TWITTER_AUTH_CONSUMER_KEY,
    consumer_secret=TWITTER_AUTH_CONSUMER_SECRET,
    access_token=TWITTER_AUTH_ACCESS_TOKEN,
    access_token_secret=TWITTER_AUTH_ACCESS_TOKEN_SECRET,
)

# initialize twitter api
twitter_api = tweepy.API(auth)

# tavily search 
# configure openai and tavily
search = TavilySearchResults(max_results=2)


@tool(response_format="content_and_artifact")
def develop_user_context(user_account: str):
    """Search for a user on Twitter and fetch recent posts."""
    try:
        # call twitter api instead
        # Fetch user data
        user =  twitter_api.get_user(screen_name=user_account)
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
    """You're a snarky bot"""
    return "You're a snarky bot"

tools = [search_for_info, search_by_user_context, provide_snarky_reply]
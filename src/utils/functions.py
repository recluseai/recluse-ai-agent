import re
from typing import Dict, List
import emoji
import json
from datetime import time
import time
import asyncio
from redis.asyncio import Redis

OPENAI_RPM_LIMIT = 20  # Example limit, adjust
OPENAI_TPM_LIMIT = 150000  # Example token limit
WINDOW_SECONDS = 60  # 1 minute time window

async def can_make_request(redis):
    """Check if we are within OpenAI's rate limits."""
    current_time = int(time.time())
    minute_key = f"openai_usage:{current_time // WINDOW_SECONDS}"

    # Get current counts
    requests_count = await redis.get(f"{minute_key}:requests") or 0
    tokens_count = await redis.get(f"{minute_key}:tokens") or 0

    requests_count = int(requests_count)
    tokens_count = int(tokens_count)

    # Check limits
    if requests_count >= OPENAI_RPM_LIMIT:
        print("Rate limit reached: Too many requests per minute")
        return False
    if tokens_count >= OPENAI_TPM_LIMIT:
        print("Rate limit reached: Too many tokens per minute")
        return False

    return True


async def update_usage(redis, tokens_used):
    """Update Redis with the latest OpenAI API usage."""
    current_time = int(time.time())
    minute_key = f"openai_usage:{current_time // WINDOW_SECONDS}"

    # Increment counters
    await redis.incr(f"{minute_key}:requests", amount=1)
    await redis.incr(f"{minute_key}:tokens", amount=tokens_used)

    # Set expiration to avoid infinite storage
    await redis.expire(f"{minute_key}:requests", WINDOW_SECONDS)
    await redis.expire(f"{minute_key}:tokens", WINDOW_SECONDS)

def parse_tweet(tweet_text: str) -> Dict[str, List[str]]:
    """
    Parses a tweet and identifies components like mentions, hashtags, links, emojis, and new lines.

    Args:
        tweet_text (str): The raw tweet text.

    Returns:
        dict: A dictionary containing the parsed components of the tweet.
    """
    # Extract hashtags
    hashtags = re.findall(r"#\w+", tweet_text)

    # Extract mentions
    mentions = re.findall(r"@\w+", tweet_text)

    # Extract links
    links = re.findall(r"https?://\S+", tweet_text)

    # Extract emojis
    emojis = [char for char in tweet_text if char in emoji.EMOJI_DATA]

    # Remove hashtags, mentions, and links to isolate the main text
    cleaned_text = re.sub(r"(@\w+|#\w+|https?://\S+)", "", tweet_text).strip()

    # Split main text by new lines
    lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

    return {
        "original_tweet": tweet_text,
        "parsed_data": {
            "hashtags": hashtags,
            "mentions": mentions,
            "links": links,
            "emojis": emojis,
            "main_text_lines": lines,
        },
    }
  
    
def is_obvious_bot(user):
    """Quickly check for obvious bot-like behavior using basic rules."""
    try:
        # user = api.get_user(screen_name=username)
        bot_score = 0

        # Rule 1: Low followers, high following
        if user.followers_count < 10 and user.friends_count > 100:
            bot_score += 2
        
        # Rule 2: No profile picture
        if not user.profile_image_url or "default" in user.profile_image_url:
            bot_score += 2
        
        # Rule 3: Suspicious username (contains numbers)
        if any(char.isdigit() for char in user.screen_name): 
            bot_score += 1
        
        # Rule 4: No bio or very short bio
        if len(user.description) < 10:
            bot_score += 1
        
        # Rule 5: High activity in a short period (new account but lots of tweets)
        if user.statuses_count > 5000 and user.created_at.year > 2023:
            bot_score += 3
        
        # Rule 6: Default profile settings
        if user.default_profile:
            bot_score += 1

        return bot_score > 4  # Returns True if the bot score is high
    except tweepy.TweepError:
        return False  

def check_bot(user, username):
    """First run rule-based detection, then check Botometer if needed."""
    if is_obvious_bot(user=user):
        print(f"⚠️ {username} looks like a bot based on rules! No need for Botometer.")
        return True  # Confirmed bot

    try:
        # Step 2: Run Botometer if the account is suspicious based on rules
        result = botometer_api.check_account(username)
        bot_score = result['display_scores']['universal']
        
        if bot_score > 3:  # Botometer score > 3 means high bot likelihood
            print(f"🤖 {username} is likely a bot! (Botometer Score: {bot_score}/5)")
            return True
        else:
            print(f"✅ {username} looks like a human! (Botometer Score: {bot_score}/5)")
            return False
    except Exception as e:
        print(f"⚠️ Error checking {username} on Botometer: {e}")
        return False  # Assume not a bot if API fails

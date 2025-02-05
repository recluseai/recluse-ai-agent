import re
from typing import Dict, List
import emoji
import json
from datetime import time

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



# Example usage
# tweet = """🚨Breaking news!

# #AIXBT are launching a large-scale giveaway!

# ➜ https://t.co/eZLbSjtVgc

# G1eS

# @cyrusfnr @Glenliuzq @DotsamaApe @22Trades22 @wushu8355 @dediewijaya11
# @sergei_serch @ConcreteXCrypto @treflipx @Erickpinguim @recluseai_ @Sirius365"""
# parsed_tweet = parse_tweet(tweet)
# print(parsed_tweet)

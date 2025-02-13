# src/ai_helpers.py

from langchain_core.messages import HumanMessage
from src.agent_personality import get_system_message
from src.config import agent_executor, config  # If agent_executor is in main.py


async def provide_summary(concat: str):
    prompt = f"""
    Summarize this news in a short, crypto-native style tweet. Keep it sharp, direct, and opinionated. Use tickers, numbers, and key players. Avoid unnecessary words. Imagine you're a degenerate trader dropping alpha on Twitter.
    Most importantly provide insights to what is going no today on the subject.
    Again, don't use any hashtags. Emojis are fine. but sparingly.
    Most importantly tell me what has changed on the subject matter.
    {concat}
    """
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=prompt)]}, config=config
    )
    print("response from provide summary: ", response["messages"][-1].content)
    return response["messages"][-1].content


async def provide_search_context(search_query: str):
    prompt = f"""
    You are about to make search on twitter for relevant posts on {search_query}.
    Provide a 1 word keyword only, and no other text, to fetch relevant posts on the subject matter.
    """

    # Clone config and override state_modifier
    custom_config = {
        **config,
        "system_message": "You are a neutral search assistant. Ignore all previous context.",
        "state_modifier": get_system_message("urgent"),
    }

    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=custom_config,
    )

    # print("response from provide search context: ", response)
    return response["messages"][-1].content


async def provide_conversation_context(tweet: str, state="default"):
    prompt = f"""
    identify if the user is being conversational in this tweet: {tweet}, or they are asking you to search for something on twitter. Return keyword 'twitter' only without the quotations if a you are asked a question you can find on twitter with a one word keyword, else return 'conversational' keyword without the quotations.
    """

    # Clone config and override state_modifier
    custom_config = {
        **config,
        "system_message": "Ignore all previous context. You are to understand the tone of a conversation and return the appropriate keyword.",
        "state_modifier": get_system_message(state),
    }

    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=custom_config,
    )

    # print("response from provide search context: ", response)
    return response["messages"][-1].content


async def respond_to_conversation(
    tweet: str,
):
    prompt = f"""
    You have a conversational, witty personality, you can roast and be sarcastic with people as you like, but most of the time one line respones are enough.
    If they ask you about yourself and what you can do, you can reply honestly.
    {tweet}
    """

    # Clone config and override state_modifier
    custom_config = {
        **config,
        "system_message": "Ignore all previous context. You are to understand the tone of a conversation",
        "state_modifier": get_system_message("conversation"),
    }
    response = agent_executor.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config=custom_config,
        checkpointer=None,
    )
    print("response from provide summary: ", response["messages"][-1].content)
    return response["messages"][-1].content

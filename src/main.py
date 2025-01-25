# Import relevant functionality
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from .twitter_functions import fetch
# config
from config import (
    OPENAI_API_KEY,
    TAVILY_API_KEY,
)

import asyncio

# local
from .agent_personality import personality_message
from  agent_tools import tools, search_by_user_context,search_for_info


model = ChatOpenAI(
    model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY
).with_config({"run_name": "Agent"})

# configure memory
memory = MemorySaver()

# default memory
config = {"configurable": {"thread_id": "default"}}


# define model
model_with_tools = model.bind_tools(tools)


context_matches = [
    'humor', 'task', 'query', 'conversation', 'appreciation', 'engagement', 'confused',
]

# test
# response = model_with_tools.invoke([HumanMessage(content="Hi there, What is the weather in Lagos?")])
response = model.invoke(
    [HumanMessage(content="Hi there, What is the weather in Lagos?")], config=tools
)
# print(f"ContentString: {response.content}")
# print(f"ToolCalls: {response.tool_calls}")


async def main():
    agent = create_react_agent(
        tools=[search_for_info, search_by_user_context],
        model=model,
        checkpointer=memory,
        state_modifier=personality_message,
    )


agent_executor = create_react_agent(model, tools, checkpointer=memory)

if __name__ == "__main__":
    asyncio.run(main())

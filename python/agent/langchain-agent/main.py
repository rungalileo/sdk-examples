from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
import os

# Load environment variables (e.g., API keys)
load_dotenv()


# Define a tool for the agent to use
@tool
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}! 👋"


# Use the Galileo context manager to specify project and log stream
with galileo_context(project="langchain-docs", log_stream="my_log_stream"):
    agent = initialize_agent(
        tools=[greet],
        llm=ChatOpenAI(model="gpt-4", temperature=0.7, callbacks=[GalileoCallback()]),
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    if __name__ == "__main__":
        result = agent.invoke({"input": "Say hello to Erin"})
        print(f"\nAgent Response:\n{result}")

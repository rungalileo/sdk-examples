import os

from dotenv import load_dotenv

# Load environment variables before anything imports galileo so the env vars
# are present when pydantic-settings initialises GalileoConfig.
load_dotenv()

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from galileo import galileo_context
from splunk_ao.handlers.langchain import SplunkAOCallback


# Define a tool for the agent to use
@tool
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}! 👋"


# Use the Galileo context manager to specify project and log stream
with galileo_context(
    project=os.environ["SPLUNK_AO_PROJECT"],
    log_stream=os.environ["SPLUNK_AO_LOG_STREAM"],
):
    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.7,
    )

    agent = create_agent(
        model=llm,
        tools=[greet],
        system_prompt="You are a helpful assistant.",
    )

    if __name__ == "__main__":
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "Say hello to Erin"}]},
            config={"callbacks": [SplunkAOCallback()]},
        )
        # Extract the final assistant message
        final = result["messages"][-1].content
        print(f"\nAgent Response:\n{final}")

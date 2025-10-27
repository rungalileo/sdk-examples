import os

from strands import Agent, tool
from strands.telemetry import StrandsTelemetry
from strands_tools import calculator, current_time

# Load environment variables from the .env file
from dotenv import load_dotenv

load_dotenv(override=True)

# Export the Galileo OTel API endpoint for OTel
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = os.environ.get("GALILEO_API_ENDPOINT", "https://api.galileo.ai/otel/traces")

# Export the Galileo OTel headers pointing to the correct API key, project, and log stream
headers = {
    "Galileo-API-Key": os.environ["GALILEO_API_KEY"],
    "project": os.environ["GALILEO_PROJECT"],
    "logstream": os.environ["GALILEO_LOG_STREAM"],
}

os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = ",".join([f"{k}={v}" for k, v in headers.items()])

# Setup telemetry for the Strands agent using Galileo as the OTel backend
strands_telemetry = StrandsTelemetry()
strands_telemetry.setup_otlp_exporter()

# Uncomment this line to see the OTel output in the console
# strands_telemetry.setup_console_exporter()


# This agent code is from the simple quickstart from the Strands documentation
# https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/


# Define a custom tool as a Python function using the @tool decorator
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0

    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())


# Create an agent with tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent(tools=[calculator, current_time, letter_counter])

# Ask the agent a question that uses the available tools
message = """
I have 4 requests:

1. What is the time right now?
2. Calculate 3111696 / 74088
3. Tell me how many letter R's are in the word "strawberry" 🍓
"""
agent(message)

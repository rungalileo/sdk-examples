# A script to generate log streams

from dotenv import load_dotenv

load_dotenv(override=True)

import json
import random
from typing import Any

from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback

from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import Callbacks
from langchain_core.messages import HumanMessage

from src.galileo_langgraph_fsi_agent.agents.supervisor_agent import (
    create_supervisor_agent,
)

import uuid

with open("./dataset.json", "r", encoding="utf-8") as f:
    dataset_content = json.load(f)

print(f"Starting to log {len(dataset_content)} interactions...")
row_number = 1

# Build the agent graph
supervisor_agent = create_supervisor_agent()

for row in dataset_content:
    print(f"Processing row {row_number} of {len(dataset_content)}")

    user_input = row["input"]

    # Randomly start a new session - this way sometimes we have multiple interactions in the same session.
    # Need a 50% chance to start a new session.
    # If this is row 1, always start a new session.
    if row_number == 1 or random.random() < 0.5:
        EXTERNAL_ID = str(uuid.uuid4())
        galileo_context.start_session(external_id=EXTERNAL_ID)

    # Create the callback. This needs to be created in the same thread as the session
    # so that it uses the same session context.
    galileo_callback = GalileoCallback()

    config: dict[str, Any] = {"configurable": {"thread_id": random.randint(1, 1000)}}
    callbacks: Callbacks = [galileo_callback]  # type: ignore

    # Set up the config for the streaming response
    runnable_config = RunnableConfig(callbacks=callbacks, **config)

    messages: dict[str, Any] = {"messages": [HumanMessage(content=user_input)]}
    supervisor_agent.invoke(input=messages, config=runnable_config)

    # Wait for a random time between 20-60 seconds before the next interaction
    # wait_time = random.randint(20, 60)
    # time.sleep(wait_time)

    # increment the row number
    row_number += 1

print("All interactions logged successfully.")

# A script to generate log streams

# Load the dataset.json
from datetime import datetime
import json
import uuid

from galileo import galileo_context

from app import chat_with_llm, chat_history

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv(override=True)

with open("../dataset.json", "r", encoding="utf-8") as f:
    dataset_content = json.load(f)

print(f"Starting to log {len(dataset_content)} interactions...")
row_number = 1

for row in dataset_content:
    # Remove all user and assistant messages from the chat history
    system_prompt = chat_history[0]["content"]
    chat_history.clear()
    chat_history.append({"role": "system", "content": system_prompt})

    print(f"Processing row {row_number} of {len(dataset_content)}")
    row_number += 1

    user_input = row["input"]
    print(f"User Input: {user_input}")

    logger = galileo_context.get_logger_instance()
    session_name = f"LLM Chatbot session - {datetime.now().isoformat()}"
    logger.start_session(session_name, external_id=str(uuid.uuid4()))

    # Start a trace for the user input
    logger.start_trace(name="Conversation step", input=user_input)

    # Call the chat_with_llm function to get a response from the LLM
    response = chat_with_llm(user_input)
    # Print the response from the LLM
    print(f"LLM Response: {response}")

    # Conclude and flush the logger after each interaction
    # so that a new trace is started each time
    logger.conclude(output=response)
    logger.flush()

    # Wait for a random time between 20-60 seconds before the next interaction
    # wait_time = random.randint(20, 60)
    # time.sleep(wait_time)

print("All interactions logged successfully.")

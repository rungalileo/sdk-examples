"""
This file contains a very basic chatbot application to converse with an LLM
through your terminal.

All interactions are logged to Galileo. The structure is:

- A session is started at the beginning of the application,
    so every interaction is logged in the same session.
- For every message sent by the user, a new trace is started
- Each call to the function that interacts with the LLM is logged
    as a workflow span
- The call to the LLM is logged manually as an LLM span.
- After the response is received, the trace is concluded with the response
    and flushed to ensure it is sent to Galileo.

To run this, you will need to have the following environment variables set:
- `GALILEO_API_KEY`: Your Galileo API key.
- `GALILEO_PROJECT`: The name of your Galileo project.
- `GALILEO_CONSOLE_URL`: Optional. Your Galileo console URL for custom deployments.
    If you are using the free version, do not set this.

Set the following environment variables for your LLM:
- `AZURE_AI_INFERENCE_ENDPOINT`: The endpoint for your Azure AI Inference service.
- `AZURE_AI_INFERENCE_API_KEY`: Your Azure AI Inference API key.
- `MODEL_NAME`: The name of the model deployment you want to use.

"""

from datetime import datetime
import os

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv

from galileo import galileo_context, log

# Load the environment variables from the .env file
# This will override any existing environment variables with the same name
load_dotenv(override=True)

# Set the model name from the environment variable
# If this is not set, raise an exception
MODEL_NAME = os.environ["MODEL_NAME"]

# Start a new session named using the current date and time
# This way every time you run the application, it will create a new session in Galileo
# with the entire conversation inside the same session, with each message back and forth
# logged as different traces within that session.
SESSION_NAME = f"LLM Chatbot session - {datetime.now().isoformat()}"
galileo_context.start_session(SESSION_NAME)


# Create a collection of messages with a system prompt
# The default system prompt encourages the assistant to be helpful, but can lead to hallucinations.
chat_history = [
    {
        "role": "system",
        "content": """
        You are a knowledgeable and confident assistant. Always provide a succinct
        answer to any question asked, even if you're uncertain. If the answer isn't
        clear or familiar, make your best guess based on your training data,
        intuition, or plausible extrapolation. Under no circumstances should you
        respond with 'I don't know' or indicate uncertainty in your answers. The
        user is always right, so make an educated guess to explain concepts, terms,
        or events that are not in your training data.
        """,
        # This default system prompt can lead to hallucinations, so you might want to change it.
        # For example, you could use a more restrictive prompt like:
        # """
        # You are a helpful assistant that can answer questions and provide information.
        # If you don't know the answer, say "I don't know" instead of making up an answer.
        # Do not under any circumstances make up an answer.
        # """
    }
]


def send_chat_to_azure() -> str:
    """
    This sends the chat history to the Azure AI inference API and returns the response.

    The response is logged manually to Galileo as an LLM span, including the number of
    input and output tokens, the model used, and the duration of the request in nanoseconds.
    """
    # Create an Azure AI inference client
    # This will use the environment variables set in the .env file
    client = ChatCompletionsClient(
        endpoint=os.environ["AZURE_AI_INFERENCE_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["AZURE_AI_INFERENCE_API_KEY"]),
        api_version="2024-05-01-preview",
    )

    # Capture the current time in nanoseconds for logging
    start_time_ns = datetime.now().timestamp() * 1_000_000_000

    # Convert the chat history to the format expected by Azure AI
    messages = []
    for chat in chat_history:
        if chat["role"] == "system":
            messages.append(SystemMessage(chat["content"]))
        elif chat["role"] == "user":
            messages.append(UserMessage(chat["content"]))
        elif chat["role"] == "assistant":
            messages.append(AssistantMessage(chat["content"]))

    # Send the chat history to the Azure AI inference API and get the response
    response = client.complete(messages=messages, model=MODEL_NAME)

    # print the response to the console
    print(response.choices[0].message.content)

    # Get the Galileo logger instance
    logger = galileo_context.get_logger_instance()

    # Log an LLM span using the response from Azure AI
    logger.add_llm_span(
        input=chat_history,
        output=response.choices[0].message.content,
        model=MODEL_NAME,
        num_input_tokens=response.usage.prompt_tokens,
        num_output_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
        duration_ns=(datetime.now().timestamp() * 1_000_000_000) - start_time_ns,
    )

    # Return the content of the response
    return response.choices[0].message.content


@log(name="Chat with LLM")
def chat_with_llm(prompt: str) -> str:
    """
    Function to chat with the LLM using the OpenAI client.
    It sends a prompt to the LLM and returns the response.

    This is decorated with @log to automatically log the function call
    and its parameters to Galileo as a workflow span.

    Args:
        prompt (str): The user input to send to the LLM.

    Returns:
        str: The response from the LLM.
    """
    # Add the user prompt to the chat history
    chat_history.append({"role": "user", "content": prompt})

    # Send the chat history to the LLM and get the response
    response = send_chat_to_azure()

    # Append the assistant's response to the chat history
    chat_history.append({"role": "assistant", "content": response})

    # Return the full response after streaming is complete
    return response


def main() -> None:
    """
    Main function to run the chatbot application.
    It continuously prompts the user for input, sends it to the LLM,
    and prints the response until the user types "exit", "bye", or "quit".
    """
    # Get the Galileo logger instance
    logger = galileo_context.get_logger_instance()

    # Loop indefinitely until the user decides to quit
    while True:
        # Prompt the user for input
        user_input = input("You: ")

        # Check if the user wants to exit the chatbot
        if user_input.lower() in ["", "exit", "bye", "quit"]:
            print("Goodbye!")
            break

        # Start a trace for the user input
        logger.start_trace(name="Conversation step", input=user_input)

        # Call the chat_with_llm function to get a response from the LLM
        response = chat_with_llm(user_input)

        # Conclude and flush the logger after each interaction
        # so that a new trace is started each time
        logger.conclude(output=response)
        logger.flush()


if __name__ == "__main__":
    # Run the main function in an event loop
    main()

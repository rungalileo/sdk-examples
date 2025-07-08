"""
This file contains a very basic chatbot application to converse with an LLM
through your terminal. It uses a choice of LLM SDKs that you can configure:
- Any OpenAI-compatible LLM, such as OpenAI or Ollama
- Anthropic
- Azure AI Inference

All interactions are logged to Galileo. The structure is:

- A session is started at the beginning of the application,
    so every interaction is logged in the same session.
- For every message sent by the user, a new trace is started
- Each call to the function that interacts with the LLM is logged
    as a workflow span
- The call to the LLM is logged as an LLM span.
    - If you are using OpenAI, then the Galileo OpenAI client is used which
        logs the span automatically.
    - If you are using Anthropic or Azure AI, then the span is logged manually.
- After the response is received, the trace is concluded with the response
    and flushed to ensure it is sent to Galileo.

To run this, you will need to have the following environment variables set:
- `GALILEO_API_KEY`: Your Galileo API key.
- `GALILEO_PROJECT`: The name of your Galileo project.
- `GALILEO_CONSOLE_URL`: Optional. Your Galileo console URL for custom deployments.
    If you are using the free version, do not set this.

- To select the LLM you want to use, set the `LLM` environment variable
    to one of the following values:
    - `OpenAI`: Use the OpenAI or Ollama client.
    - `Anthropic`: Use the Anthropic client.
    - `Azure`: Use the Azure AI Inference client.

If you are using OpenAI or a compatible LLM, you will need to set the following
environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key. If you are using Ollama then set this to ollama.
- `OPENAI_BASE_URL`: The base URL for your OpenAI API. If you are using Ollama,
    set this to "http://localhost:11434/v1".

If you are using Anthropic, you will need to set the following environment variable:
- `ANTHROPIC_API_KEY`: Your Anthropic API key.

If you are using Azure AI Inference, you will need to set the following environment variables:
- `AZURE_AI_INFERENCE_ENDPOINT`: The endpoint for your Azure AI Inference service.
- `AZURE_AI_INFERENCE_API_KEY`: Your Azure AI Inference API key.

Finally, you need to set the model name to the model used by the LLM you want to use.
- `MODEL_NAME`: The name of the model you want to use.

"""

from datetime import datetime
import os

from anthropic import Anthropic

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv

from galileo import galileo_context, log
from galileo.openai import OpenAI

# Load the environment variables from the .env file
# This will override any existing environment variables with the same name
load_dotenv(override=True)

# Set the model name from the environment variable
# If this is not set, raise an exception
MODEL_NAME = os.environ["MODEL_NAME"]

# Get the selected LLM from the environment variable
LLM = os.environ["LLM"].lower()

# Check if the LLM is valid
if LLM not in ["openai", "anthropic", "azure"]:
    raise ValueError(
        f"Invalid LLM selected: {LLM}. "
        "Please set the LLM environment variable to one of: OpenAI, Anthropic, or Azure."
    )

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
        You are a helpful assistant that can answer questions and provide information.
        If you are not sure about the question, then try to answer it to the best of your ability,
        including extrapolating or guessing the answer from your training data.
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


def send_chat_to_anthropic() -> str:
    """
    This sends the chat history to the Anthropic API and returns the response.

    The response is logged manually to Galileo as an LLM span, including the number of
    input and output tokens, the model used, and the duration of the request in nanoseconds.
    """
    # Create an Anthropic client
    # This will use the environment variables set in the .env file
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Capture the current time in nanoseconds for logging
    start_time_ns = datetime.now().timestamp() * 1_000_000_000

    # Convert the chat history to the format expected by Anthropic
    # This removes the system prompt to send separately as
    # a parameter to the messages.create method.
    chat_history_anthropic = []
    system_prompt = ""
    for chat in chat_history:
        if chat["role"] == "system":
            system_prompt = chat["content"]
        else:
            chat_history_anthropic.append(
                {"role": chat["role"], "content": chat["content"]}
            )

    # Send the chat history to the Anthropic API and get the response
    response = client.messages.create(
        max_tokens=1024,
        messages=chat_history_anthropic,
        system=system_prompt,
        model=MODEL_NAME,
    )

    # Print the response to the console
    print(response.content[0].text)

    # Get the Galileo logger instance
    logger = galileo_context.get_logger_instance()

    # Log an LLM span using the response from Anthropic
    logger.add_llm_span(
        input=chat_history,
        output=response.content[0].text,
        model=MODEL_NAME,
        num_input_tokens=response.usage.input_tokens,
        num_output_tokens=response.usage.output_tokens,
        total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        duration_ns=(datetime.now().timestamp() * 1_000_000_000) - start_time_ns,
    )

    # Return the content of the response
    return response.content[0].text


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


def send_chat_to_openai() -> str:
    """
    This sends the chat history to the OpenAI API and returns the response.

    The streamed response is also printed to the console in real-time.

    The response is logged automatically to Galileo as an LLM span, including the number of
    input and output tokens, the model used, and the duration of the request in nanoseconds.
    This is handled by the Galileo OpenAI client
    """
    # Create an OpenAI client
    # This will use the environment variables set in the .env file, so can connect to
    # any OpenAI-compatible API, such as OpenAI or Ollama
    client = OpenAI()

    # Send the prompt to the LLM and get a streaming response
    # This uses the Galileo OpenAI client which is configured to log the request and response
    # to Galileo automatically in an LLM span, along with token and other information.
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=chat_history,
        stream=True
    )

    # Stream the response to the console
    # Also capture the full response to add to the chat history and return
    full_response = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            # Write the chunk to the terminal
            print(chunk.choices[0].delta.content, end="", flush=True)

            # Append the chunk content to the full response
            full_response += chunk.choices[0].delta.content

    print()  # Print a newline for better formatting

    return full_response


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
    # Depending on the selected LLM, call the appropriate function
    if LLM == "openai":
        print("Sending chat to OpenAI...")
        response = send_chat_to_openai()
    elif LLM == "anthropic":
        print("Sending chat to Anthropic...")
        response = send_chat_to_anthropic()
    elif LLM == "azure":
        print("Sending chat to Azure...")
        response = send_chat_to_azure()
    else:
        raise ValueError(f"Unsupported LLM: {LLM}")

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

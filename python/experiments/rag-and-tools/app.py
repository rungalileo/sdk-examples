import json

from galileo import log, galileo_context

from galileo.openai import OpenAI

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


# A mock RAG retriever function
@log(span_type="retriever")
def retrieve_horoscope_data(sign):
    """
    Mock function to simulate retrieving horoscope data for a given sign.
    This is decorated with logging for tracing a retriever span.
    """
    horoscopes = {
        "Aquarius": [
            "Next Tuesday you will befriend a baby otter.",
            "Next Tuesday you will find a dollar on the ground.",
        ],
        "Taurus": [
            "Next Tuesday you will find a four-leaf clover.",
            "Next Tuesday you will have a great conversation with a stranger.",
        ],
        "Gemini": [
            "Next Tuesday you will learn to juggle.",
            "Next Tuesday you will discover a new favorite book.",
        ],
    }
    return horoscopes.get(sign, ["No horoscope available."])


@log(span_type="tool")
def get_horoscope(sign):
    """
    Tool function to get a horoscope for a given astrological sign.
    """
    return "\n".join(retrieve_horoscope_data(sign))


# Define a list of callable tools for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_horoscope",
            "description": "Get today's horoscope for an astrological sign.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sign": {
                        "type": "string",
                        "description": "An astrological sign like Taurus or Aquarius",
                    },
                },
                "required": ["sign"],
            },
        },
    },
]

# Map tool names to their implementations
available_tools = {"get_horoscope": get_horoscope}


# Create the OpenAI client
client = OpenAI()


def call_llm(messages):
    """
    Call the LLM with the provided messages and tools.
    """
    return client.chat.completions.create(
        model="gpt-5.1",
        tools=tools,
        messages=messages,
    )


def get_users_horoscope(sign: str) -> str:
    """
    Get the user's horoscope
    """
    # Create a running message history list we will add to over time
    message_history = [
        {
            "role": "system",
            "content": """
            You are a helpful assistant that provides horoscopes.
            Provide a flowery response based off any information retrieved.
            Include typical horoscope phrases, and characteristics of
            the sign in question.
            """,
        },
        {"role": "user", "content": f"What is my horoscope? I am {sign}."},
    ]

    # Prompt the model with tools defined
    response = call_llm(message_history)

    # Call any tools the model requested
    completion_tool_calls = response.choices[0].message.tool_calls

    if completion_tool_calls:
        # Add any tool calls to the message history
        message_history.append(
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in completion_tool_calls
                ],
            }
        )

        for call in completion_tool_calls:
            # Get the tool to call and its arguments
            tool_to_call = available_tools[call.function.name]
            args = json.loads(call.function.arguments)

            # Call the tool
            tool_result = tool_to_call(**args)

            # Add the tool result to the message history
            message_history.append(
                {
                    "role": "tool",
                    "content": tool_result,
                    "tool_call_id": call.id,
                    "name": call.function.name,
                }
            )

        # Now we call the model again, with the tool results included
        response = call_llm(message_history)

    # Return the final response from the model
    return response.choices[0].message.content


def main():
    """
    Get the user's horoscope
    """
    # Start a session and trace
    galileo_logger = galileo_context.get_logger_instance()
    galileo_logger.start_session("RAG with Tools Example")
    galileo_logger.start_trace(input="What is my horoscope? I am Aquarius.", name="Calling LLM with Tool")
    galileo_logger.start_trace(input="What is my horoscope? I am Aquarius.", name="Calling LLM with Tool")

    response = get_users_horoscope("Aquarius")

    # Conclude the trace and flush
    galileo_logger.conclude(response)
    galileo_logger.flush()

    print(response)


if __name__ == "__main__":
    main()

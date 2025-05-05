import os

from galileo import galileo_context, openai

# If you've set your GALILEO_PROJECT and GALILEO_LOG_STREAM env vars, you can skip this step
galileo_context.init(project="your-project-id", log_stream="your-log-stream-id")

# Initialize the Galileo wrapped OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def call_openai():
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Say this is a test"}], model="gpt-4o"
    )

    return chat_completion.choices[0].message.content


# This will create a single span trace with the OpenAI call
call_openai()

import os
import time
import openai  # Using the standard OpenAI library
from galileo import GalileoLogger  # Import GalileoLogger for logging

from dotenv import load_dotenv

load_dotenv()

# Initialize the GalileoLogger
logger = GalileoLogger(project="chatbot", log_stream="test")

# Initialize the standard OpenAI client
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
)

# Start a trace
# prompt = f"Explain the following topic succinctly: Newton's First Law"
prompt = """
	1.	Explain Newton's First Law in one sentence of no more than fifteen (15) words.
	2.	Do not add any additional sentences, examples, parentheses, bullet points, or further clarifications.
	3.	Your answer must be exactly one sentence and must not exceed 15 words.
"""
trace = logger.start_trace(input=prompt)

# Record the start time for the LLM call
start_time = time.time_ns()

# Make the OpenAI API call directly
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": prompt}],
)

# Record the end time for the LLM call
end_time = time.time_ns()

# Get the response content
response_content = response.choices[0].message.content.strip()

# Log the LLM call as a span
logger.add_llm_span(
    input=prompt,
    output=response_content,
    model="gpt-4o",
    duration_ns=end_time - start_time,
    num_input_tokens=response.usage.prompt_tokens,
    num_output_tokens=response.usage.completion_tokens,
    total_tokens=response.usage.total_tokens,
)

# Conclude the trace
logger.conclude(output=response_content)

# Flush the traces to Galileo
logger.flush()

# Print the response
print(response_content)

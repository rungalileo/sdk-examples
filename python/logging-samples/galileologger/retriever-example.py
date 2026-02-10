from galileo import galileo_context # The Galileo context manager
from galileo.config import GalileoPythonConfig # For displaying the log stream URL 

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

prompt_input_data = [
    "Explain Newton's First Law like you're a dramatic movie trailer narrator.",
    "Write a silly limerick about Newton's First Law starring a very stubborn banana.",
    "Explain Newton's First Law to a 5-year-old using toys, snacks, or animals."
]

prompt_output_data = [
    "In a world where objects refuse to budge, Newton's First Law declares that things stay still—or keep moving—unless a force steps in to change their fate.",
    "There once was a banana so grand,\nWho lay very still on the land.\nIt stayed put all day,\nTill a force came its way,\nNow Newton would say, 'Just as planned!'",
    "Things like to keep doing what they're already doing. A toy will stay still or keep rolling until something, like your hand, makes it change."
]

logger = galileo_context.get_logger_instance() 

for i in range(len(prompt_input_data)):

    prompt_output = prompt_output_data[0]

    # Start a session
    session_id = logger.start_session(name="Test session with retriever span")

    # Start a new trace
    trace = logger.start_trace("This is a trace start")


    # Add a retriever span for document retrieval
    logger.add_retriever_span(
        input="Who's a good bot?",
        output=["Research shows that I am a good bot."],
        name="Document Retrieval",
        duration_ns=1000000
    )

    # Add an LLM span for generating a response
    logger.add_llm_span(
        input="Who's a good bot?",
        output="I am!",
        model="gpt-5-mini",
        name="Response Generation",
        num_input_tokens=25,
        num_output_tokens=3,
        total_tokens=28,
        duration_ns=1000000
    )


    # Conclude the trace with the final output
    logger.conclude(output="This is a trace conclude", duration_ns=1000)


    # Add another trace and span
    logger.start_trace("This is another trace start")

    logger.add_llm_span(
        input=prompt_input_data[i],
        output=prompt_output_data[i],
        model="gpt-5-mini"
    )

    logger.conclude(output="This is another trace conclude", duration_ns=1000)


    # Flush the traces to galileo
    logger.flush()


# Show link to Galileo log stream
config = GalileoPythonConfig.get()
project_url = f"{config.console_url}project/{logger.project_id}"
log_stream_url = f"{project_url}/log-streams/{logger.log_stream_id}"

print("🚀 Galileo Log Stream:")
print(log_stream_url)
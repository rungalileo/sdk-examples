from galileo import GalileoLogger
from galileo.projects import get_project
from galileo.log_streams import get_log_stream
from galileo.export import export_records
from galileo.resources.models.root_type import RootType
from galileo.config import GalileoPythonConfig  # For displaying the log stream URL

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

logger = GalileoLogger() # Create a logger instance

# Example of how to create "redacted_input", matching "SSN" as sensitive info
# ---------------------------------------------------------------------------
sensitive_info = "SSN"
user_input = "Who's a good bot SSN?"
redacted_input = user_input.replace(sensitive_info, "***")
trace = logger.start_trace(input=user_input, redacted_input=redacted_input)

logger.flush()  # send the trace to Galileo

# Example of how to create "redacted_input", matching email as sensitive info
# ---------------------------------------------------------------------------

import re # regular expression 

user_input = "This is the email: example@example.com"

email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', user_input)
sensitive_info = email_match.group() if email_match else None

if sensitive_info:
    redacted_input = user_input.replace(sensitive_info, "***")
    trace = logger.start_trace(input=user_input, redacted_input=redacted_input)
else:
    trace = logger.start_trace(input=user_input)

logger.flush() # send the trace to Galileo

# It's also possible to use a service such as https://www.private-ai.com/ to create the redacted_input

# Export the logged traces in the logstream

import os

project_name = os.getenv("GALILEO_PROJECT")
log_stream_name = os.getenv("GALILEO_LOG_STREAM")

project = get_project(name=project_name)
log_stream = get_log_stream(name=log_stream_name, project_name=project_name)

records = export_records(project_id=project.id, log_stream_id=log_stream.id, root_type=RootType.TRACE)

print(list(records))


# Show link to Galileo log stream

config = GalileoPythonConfig.get()
project_url = f"{config.console_url}project/{logger.project_id}"
log_stream_url = f"{project_url}/log-streams/{logger.log_stream_id}"

print("🚀 Galileo Log Stream:")
print(log_stream_url)


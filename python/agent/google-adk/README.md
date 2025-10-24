# Google ADK + OpenTelemetry Example Project

This is an example project demonstrating how to use Galileo with the Google ADK. This uses the simple [quickstart from the Google ADK documentation](https://google.github.io/adk-docs/get-started/python/#create-an-agent-project), and adds Galileo logging.

## Getting Started

To get started with this project, you'll need to have Python 3.9 or later installed. You can then install the required dependencies in a virtual environment:

```bash
pip install -r requirements.txt
```

## Configure environment variables

You will need to configure environment variables to use this project. Copy the `.env.example` file to `.env`, then update the environment variables in the `.env` file with your Google and Galileo values:

```ini
# Gemini environment variables
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=

# Galileo environment variables
GALILEO_API_ENDPOINT=
GALILEO_API_KEY=
GALILEO_PROJECT=
GALILEO_LOG_STREAM=
```

For the `GALILEO_API_ENDPOINT`, this is different to the console URL that you would normally use. If you are using `app.galileo.ai` for example, the endpoint is `https://api.galileo.ai/otel/traces`.

See the [Galileo OTel and OpenInference documentation](https://v2docs.galileo.ai/sdk-api/third-party-integrations/opentelemetry-and-openinference) for more details.

## Usage

Once the dependencies are installed, you can run the example application using the `adk` command:

```bash
adk run my_agent
```

Traces will be captured and logged to Galileo.

## Project Structure

The project structure is as follows:

```folder
google-adk/
├── my_agent/          # The main agent application
│   ├── __init__.py
│   ├── agent.py
│   └── env.example    # List of environment variables
├── requirements.txt   # Python project requirements
└── README.md          # Project documentation
```

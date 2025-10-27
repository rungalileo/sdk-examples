# Strands Agents + OpenTelemetry Example Project

This is an example project demonstrating how to use Galileo with the [Strands Agent SDK](https://strandsagents.com/latest/), using AWS Bedrock as the LLM provider. This uses the simple [quickstart from the Strands Agents documentation](https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/), and adds Galileo logging.

## Getting Started

To get started with this project, you'll need to have Python 3.9 or later installed. You can then install the required dependencies in a virtual environment:

```bash
pip install -r requirements.txt
```

## Configure environment variables

You will need to configure environment variables to use this project. Copy the `.env.example` file to `.env`, then update the environment variables in the `.env` file with your AWS and Galileo values:

```ini
# AWS environment variables
AWS_BEARER_TOKEN_BEDROCK=

# Galileo environment variables
# GALILEO_API_ENDPOINT=    # Optional, only set this if you are using a custom Galileo deployment
GALILEO_API_KEY=
GALILEO_PROJECT=
GALILEO_LOG_STREAM=
```

For the `GALILEO_API_ENDPOINT`, you only need to set this if you are using a custom Galileo deployment. There is no need to set this if you ae using [app.galileo.ai](https://app.galileo.ai). This endpoint is different to the console URL that you would normally use. See the [Galileo OpenTelemetry documentation](https://v2docs.galileo.ai/sdk-api/third-party-integrations/opentelemetry-and-openinference#self-hosted-deployments) for more details.

## Usage

Once the dependencies are installed, you can run the example application:

```bash
python agent.py
```

Traces will be captured and logged to Galileo.

## Project Structure

The project structure is as follows:

```folder
strands-agents/
├─ env.example         # List of environment variables
├── agent.py           # The main agent application
├── requirements.txt   # Python project requirements
└── README.md          # Project documentation
```

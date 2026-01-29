# PydanticAI Example Project

This is an example project demonstrating how to use Galileo with PydanticAI. It showcases an enterprise customer support agent with tools for looking up customer data, checking order status, creating support tickets, and processing refunds.

The example uses the Galileo SDK's built-in OpenTelemetry support combined with PydanticAI's native instrumentation to send traces to Galileo for observability.

## Getting Started

To get started with this project, you'll need to have Python 3.11 or later installed. You can then install the required dependencies using uv:

```bash
uv sync
```

## Usage

Once the dependencies are installed, you can run the example application:

```bash
uv run src/main.py
```

## Project Structure

The project structure is as follows:

```
pydantic-ai-support-agent/
├── src/                 # Main application files
│   └── main.py
├── pyproject.toml       # Project configuration file
├── README.md            # Project documentation
└── .env.example         # List of environment variables
```

# Using Galileo with Weather Vibes Agent
This document explains how to use Galileo for evaluating and monitoring the Weather Vibes agent.

## What is Galileo?
[Galileo](https://www.rungalileo.io/) is an AI observability and evaluation platform that helps you:
- Track agent behavior
- Collect and analyze traces
- Evaluate agent performance
- Identify areas for improvement
- Monitor production deployments

## Setup
### 1. Install Galileo SDK

```bash
pip install -r requirements-galileo.txt
```

### 2. Configure Galileo details

Create or edit your `.env` file and add your Galileo details:

```
# Galileo Environment Variables
GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
GALILEO_LOG_STREAM=your-galileo-log-stream       # The name of the log stream you want to use for logging.

# Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
# GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo
```

You can get your API key from the Galileo dashboard.

## Running the Galileo-Instrumented Agent
Run the agent with Galileo instrumentation:

```bash
python galileo_agent.py "San Francisco"
```

You can use all the same command-line arguments as the regular agent:

```bash
python galileo_agent.py --location "Tokyo" --units imperial --mood relaxing --verbose
```

## Understanding the Spans
The Galileo-instrumented version of the agent includes several span types.  Learn more about spans, the atomic unit of logging in Galileo, [here](https://v2docs.galileo.ai/getting-started/logging).

1. **Workflow Span** (`workflow`):
   - Captures the main agent workflow in `process_request`
   - Shows how the agent processes the request end-to-end
   - Also used for the main agent orchestration function

2. **Tool Spans** (`tool`):
   - Individual tool executions:
     - `weather_tool`: WeatherAPI call
     - `recommendations_tool`: Weather-based recommendations generation
     - `youtube_tool`: YouTube video search

3. **LLM Span** (`llm`):
   - Used when a span invokes an LLM call
   - Currently not used in this agent but available for future LLM integrations

4. **Retriever Span** (`retriever`):
   - Used when a span is retrieving data
   - Currently not used in this agent but available for future retrieval operations

## Viewing Traces in Galileo
After running the agent, you can view the traces in the Galileo dashboard. The traces will show:
- Request and response data for each span
- Execution time for each component
- Hierarchical view of the agent's workflow
- Input/output data flow between components

## Customizing Instrumentation
You can add more spans or customize existing ones by modifying `agent.py`:
1. **Adding LLM spans**: If you implement LLM-based tools, use `@log(span_type="llm")` decorators
2. **Adding retrieval spans**: For document retrieval functions, use `@log(span_type="retriever")` decorators
3. **Custom span names**: Modify the `name` parameter in decorators for better organization

## Using Galileo for Evaluation
You can use Galileo's evaluation features to:
1. **Create eval datasets**: Build a set of test inputs for your agent
2. **Define metrics**: Set up metrics to measure agent performance
3. **Run evaluations**: Test your agent against the datasets
4. **Analyze results**: Identify strengths and weaknesses
5. **Improve the agent**: Make targeted improvements based on insights

## Troubleshooting
If you encounter issues with Galileo:
- Check that your API key is correctly set in the environment
- Ensure the Galileo SDK is properly installed
- Verify that your spans are correctly configured
- Check the Galileo documentation for more information

For more information, visit the [Galileo documentation](https://v2docs.galileo.ai/what-is-galileo). 
# LangGraph + OpenTelemetry + Galileo Integration Guide

This example shows how to add **observability** to your LangGraph AI workflows using OpenTelemetry and Galileo. If you're new to these tools, think of this as adding "X-ray vision" to your AI application so you can see exactly what's happening inside.

## 🤔 What Are These Tools?

### OpenTelemetry (OTel)
OpenTelemetry is like a **diagnostic system** for your code. It creates "traces" that show:
- What functions/operations ran
- How long each step took
- What data flowed through your system
- Where errors occurred

Think of a trace like a detailed timeline of everything that happened when processing a user request.

### OpenInference
OpenInference is a **specialized version** of OpenTelemetry that understands AI frameworks like LangChain and LangGraph. It automatically creates meaningful traces for AI operations without you having to write extra code.

### Galileo
Galileo is an AI Reliability and Observability tool that helps developers at scale build reliable AI tooling. Instead of traces just being printed to your terminal, Galileo gives you:

## What this example shows

This example demonstrates:
- **Automatic tracing**: OpenInference automatically traces your LangGraph workflow
- **Custom tracing**: How to add your own detailed spans with attributes and events
- **Multiple destinations**: Traces go to both your console (for debugging - optional) and Galileo (for analysis)
- **Real-world setup**: Proper authentication and configuration for production use

## Prerequisites

Before you start, you'll need:

- **Python 3.12+**: [Download from python.org](https://www.python.org/downloads/)
- **UV Package Manager**: [Install UV](https://docs.astral.sh/uv/getting-started/installation/) (faster alternative to pip)
- **Galileo Account**: [Sign up for free](https://app.galileo.ai) to get:
  - API key
- **Basic understanding**: Familiarity with Python and environment variables
- [OpenAI API Key](https://openai.com/api/)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rungalileo/sdk-examples
   cd /python/agent/langgraph-otel
   ```

2. **Install dependencies using UV**:
   ```bash
   uv sync
   ```

   This will install all required dependencies including:
   - `langgraph` for state graph workflows
   - `opentelemetry-*` packages for instrumentation
   - `python-dotenv` for environment variable management

## Configuration

### Step 3: Set up Galileo

1. **Create a Galileo account** at [app.galileo.ai](https://app.galileo.ai) if you haven't already

2. **Get your API key**:
   - Log into Galileo dashboard
   - Click on your profile/settings
   - Generate or copy your API key

3. **Create a project**:
   - In the Galileo dashboard, create a new project
   - Give it a name like "Langgraph-OTel" 
   - Note the project name - you'll use this in your `.env` file

4. **Create your `.env` file**:
   ```bash
   cp .env.example .env
   ```

5. **Edit your `.env` file** with your actual values:
   ```bash
   # Replace with YOUR actual API key from Galileo dashboard
   GALILEO_API_KEY=your_actual_api_key_here
   
   # Replace with YOUR project name from step 3
   GALILEO_PROJECT=LangGraph Demo
   
   # This organizes traces within your project (you can use any name - for the sake of ours, we'll call it `development`')
   GALILEO_LOG_STREAM=development
   ```

### Important Notes

- **Never commit your `.env` file** - it contains your API keys!
- **Project names are case-sensitive** - use exactly what you created in Galileo
- **Log streams** help organize traces (like folders) - create any name you want

## Running the example

### Step 4: Run It!

```bash
uv run python main.py
```

### What you'll see

The program does several things:
1. Sets up OpenTelemetry with your Galileo credentials
2. Applies automatic instrumentation to LangGraph 
3. Runs a simple workflow: "hello world" → "PROCESSED: HELLO WORLD"
4. Sends detailed traces to both console and Galileo

**Console Output:**
```
OTEL Headers: Galileo-API-Key=your_key,project=YourProject,logstream=development
✓ LangGraph instrumentation applied - automatic spans will be created
LangGraph result: {'query': 'hello world', 'response': 'Processed: HELLO WORLD'}
✓ Execution complete - check Galileo for traces in your project/log stream

# Followed by detailed JSON trace data...
```

### Understanding the Traces

You'll see traces for:
- **LangGraph**: The main workflow execution
- **initial**: The first node (validates input)
- **process**: The second node (transforms input)
- **initial_node**: Your custom span with attributes
- **processing_node**: Your custom span with events

Each trace shows:
- ⏱️ **Timing**: How long each operation took
- 🏷️ **Attributes**: Key-value data (like input text)
- 📝 **Events**: Breadcrumb-style log messages
- 🧵 **Relationships**: Parent-child span connections

### 🔍 Viewing Traces in Galileo

1. **Open Galileo**: Go to [app.galileo.ai](https://app.galileo.ai) and log in

2. **Navigate to your project**: Click on the project you created (e.g., "LangGraph Demo") and then the relevant Log stream name. 

3. **Find your traces**: Look for traces with names like:


4. **Explore the timeline**: Click on any trace to see:
   - Detailed attributes and events
   - Hierarchical span relationships

**Pro tip**: Traces may take 30-60 seconds to appear in Galileo after execution.
Refresh the screen to see recent changes and updates.

## Code structure

### Main components

```
langgraph-otel/
├── main.py           # Main workflow implementation
├── pyproject.toml    # Project dependencies and metadata
├── .env.example      # Environment variable template
└── README.md         # This file
```

### Workflow architecture

The example implements a simple two-node LangGraph workflow:

1. **Initial Node**: Receives and validates the input query
2. **Processing Node**: Transforms the query (converts to uppercase)

Each node is instrumented with OpenTelemetry spans that capture:
- Input parameters as span attributes
- Processing events and milestones
- Execution timing and metadata

### OpenTelemetry integration

#### Span structure

```python
def initial_node(state: AgentState):
    # Child of any current span; here we start a dedicated one per node
    with tracer.start_as_current_span("initial_node") as span:
        q = state.get("query", "")
        span.set_attribute("input.query", q)
        # span events are great for breadcrumbs
        span.add_event("received_query", {"len": len(q)})
        # Must return a partial state update
        return {"query": q}
```

#### Tracer configuration

```python
# Configure OpenTelemetry
resource = Resource.create({"service.name": "langgraph-agent"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
```

## Observability

### Viewing traces

#### Console output
Traces are automatically displayed in the console during execution, showing:
- Span names and timing
- Attributes and events
- Parent-child relationships

#### Galileo console
When properly configured, traces are exported to Galileo AI where you can:
- Visualize workflow execution flow
- Analyze performance bottlenecks
- Monitor system behavior over time
- Debug failed executions

### Span attributes

The example demonstrates best practices for span attributes:
- **Small string/number values**: Preferred for indexing in backends
- **Descriptive names**: Use dot notation (e.g., `input.query`, `processed.preview`)
- **Relevant metadata**: Include data that aids in debugging and analysis

### Span events

Events provide breadcrumb-style logging within spans:
- `received_query`: Logged when input is received
- `computed_response`: Logged when processing completes

## Troubleshooting

### Common issues

#### 1. Missing environment variables
```
Error: GALILEO_API_KEY not found
```
**Solution**: Ensure your `.env` file is properly configured and located in the project root.

#### 2. Network connectivity
```
Error: Failed to export traces
```
**Solution**: 
- Verify internet connectivity
- Check `GALILEO_CONSOLE_URL` if using custom deployment
- Ensure firewall allows OTLP exports

#### 3. Authentication errors
```
Error: 403 Forbidden
```
**Solution**:
- Verify `GALILEO_API_KEY` is correct and active
- Check project permissions in Galileo dashboard

#### 4. Import errors
```
ModuleNotFoundError: No module named 'langgraph'
```
**Solution**: Ensure dependencies are installed with `uv sync`

### Debugging tips

1. **Enable Console Export**: The example includes console span output for local debugging
2. **Check Environment Loading**: Add print statements to verify `.env` variables are loaded
3. **Validate Network**: Test OTLP endpoint connectivity independently
4. **Review Logs**: Check both console output and Galileo dashboard for error details

## Advanced configuration

### Custom OTLP exporters

To use different observability backends, modify the tracer setup:

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Replace ConsoleSpanExporter with OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint="https://your-backend.com/v1/traces",
    headers={"Authorization": "Bearer your-token"}
)
provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))
```

### Additional span processors

For production use, consider batch span processing:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# More efficient for high-volume tracing
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
```

## Development

### Extending the workflow

To add new nodes to the LangGraph workflow:

1. **Define the node function** with OpenTelemetry instrumentation
2. **Add the node** to the StateGraph
3. **Configure edges** between nodes
4. **Update state schema** if needed

### Best practices

- **Span Naming**: Use descriptive, consistent names
- **Attribute Limits**: Keep attribute values small for optimal indexing
- **Error Handling**: Add span status and error information for failed operations
- **Resource Cleanup**: Ensure proper span closure in all execution paths

## Related documentation

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenTelemetry Python Guide](https://opentelemetry.io/docs/instrumentation/python/)
- [Galileo Documentation](https://v2docs.galileo.ai/)
- [UV Package Manager](https://docs.astral.sh/uv/)

## License

This example is part of the SDK examples collection and follows the same licensing terms as the parent repository.

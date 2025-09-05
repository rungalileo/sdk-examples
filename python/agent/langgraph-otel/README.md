# LangGraph OpenTelemetry Integration Example

A demonstration of instrumenting LangGraph workflows with OpenTelemetry (OTEL) for comprehensive observability and tracing. This example shows how to create spans, add events, and export trace data to observability platforms like Galileo AI.

## Features

- **LangGraph Workflow**: Simple two-node state machine with query processing
- **OpenTelemetry Integration**: Full OTEL instrumentation with custom spans and events
- **Galileo AI Integration**: Export traces to Galileo for visualization and analysis
- **Console Debugging**: Local span output for development and testing
- **Environment Configuration**: Flexible setup using environment variables

## Prerequisites

- Python >= 3.12
- [UV package manager](https://docs.astral.sh/uv/) for dependency management
- Galileo AI account (optional, for trace visualization)

## Installation

1. **Clone the repository** (if not already cloned):
   ```bash
   git clone <repository-url>
   cd sdk-examples/python/agent/langgraph-otel
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

### Environment Variables

Create a `.env` file based on the provided `.env.example`:

```bash
cp .env.example .env
```

Configure the following variables in your `.env` file:

```bash
# Galileo Environment Variables (for trace export)
GALILEO_API_KEY=your_galileo_api_key_here
GALILEO_PROJECT=your_project_name
GALILEO_LOG_STREAM=default

# Optional: Custom Galileo deployment URL
# GALILEO_CONSOLE_URL=https://app.galileo.ai

# Optional: AI model configuration
OPENAI_API_KEY=your_openai_key_here
MODEL_NAME=gpt-4
```

### Required Variables

- `GALILEO_API_KEY`: Your Galileo API key for trace export
- `GALILEO_PROJECT`: Project name in Galileo where traces will be stored
- `GALILEO_LOG_STREAM`: Log stream name (defaults to "default")

### Optional Variables

- `GALILEO_CONSOLE_URL`: Custom Galileo deployment URL (defaults to https://app.galileo.ai)
- `OPENAI_API_KEY`: OpenAI API key (for future AI integrations)
- `MODEL_NAME`: AI model name to use

## Usage

### Basic Execution

Run the example workflow:

```bash
uv run python main.py
```

This will:
1. Initialize the OpenTelemetry tracer
2. Create a LangGraph workflow with two nodes
3. Execute the workflow with a sample query
4. Output traces to console and export to Galileo (if configured)

### Expected Output

```
LangGraph result: {'query': 'hello world', 'response': 'Processed: HELLO WORLD'}
```

You'll also see detailed span information in the console showing the execution flow through each node.

## Code Structure

### Main Components

```
langgraph-otel/
├── main.py           # Main workflow implementation
├── pyproject.toml    # Project dependencies and metadata
├── .env.example      # Environment variable template
└── README.md         # This file
```

### Workflow Architecture

The example implements a simple two-node LangGraph workflow:

1. **Initial Node**: Receives and validates the input query
2. **Processing Node**: Transforms the query (converts to uppercase)

Each node is instrumented with OpenTelemetry spans that capture:
- Input parameters as span attributes
- Processing events and milestones
- Execution timing and metadata

### OpenTelemetry Integration

#### Span Structure

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

#### Tracer Configuration

```python
# Configure OpenTelemetry
resource = Resource.create({"service.name": "langgraph-agent"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)
```

## Observability

### Viewing Traces

#### Console Output
Traces are automatically displayed in the console during execution, showing:
- Span names and timing
- Attributes and events
- Parent-child relationships

#### Galileo AI Dashboard
When properly configured, traces are exported to Galileo AI where you can:
- Visualize workflow execution flow
- Analyze performance bottlenecks
- Monitor system behavior over time
- Debug failed executions

### Span Attributes

The example demonstrates best practices for span attributes:
- **Small string/number values**: Preferred for indexing in backends
- **Descriptive names**: Use dot notation (e.g., `input.query`, `processed.preview`)
- **Relevant metadata**: Include data that aids in debugging and analysis

### Span Events

Events provide breadcrumb-style logging within spans:
- `received_query`: Logged when input is received
- `computed_response`: Logged when processing completes

## Troubleshooting

### Common Issues

#### 1. Missing Environment Variables
```
Error: GALILEO_API_KEY not found
```
**Solution**: Ensure your `.env` file is properly configured and located in the project root.

#### 2. Network Connectivity
```
Error: Failed to export traces
```
**Solution**: 
- Verify internet connectivity
- Check `GALILEO_CONSOLE_URL` if using custom deployment
- Ensure firewall allows OTLP exports

#### 3. Authentication Errors
```
Error: 403 Forbidden
```
**Solution**:
- Verify `GALILEO_API_KEY` is correct and active
- Check project permissions in Galileo dashboard

#### 4. Import Errors
```
ModuleNotFoundError: No module named 'langgraph'
```
**Solution**: Ensure dependencies are installed with `uv sync`

### Debugging Tips

1. **Enable Console Export**: The example includes console span output for local debugging
2. **Check Environment Loading**: Add print statements to verify `.env` variables are loaded
3. **Validate Network**: Test OTLP endpoint connectivity independently
4. **Review Logs**: Check both console output and Galileo dashboard for error details

## Advanced Configuration

### Custom OTLP Exporters

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

### Additional Span Processors

For production use, consider batch span processing:

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# More efficient for high-volume tracing
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
```

## Development

### Extending the Workflow

To add new nodes to the LangGraph workflow:

1. **Define the node function** with OpenTelemetry instrumentation
2. **Add the node** to the StateGraph
3. **Configure edges** between nodes
4. **Update state schema** if needed

### Best Practices

- **Span Naming**: Use descriptive, consistent names
- **Attribute Limits**: Keep attribute values small for optimal indexing
- **Error Handling**: Add span status and error information for failed operations
- **Resource Cleanup**: Ensure proper span closure in all execution paths

## Related Documentation

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenTelemetry Python Guide](https://opentelemetry.io/docs/instrumentation/python/)
- [Galileo AI Documentation](https://docs.galileo.ai/)
- [UV Package Manager](https://docs.astral.sh/uv/)

## License

This example is part of the SDK examples collection and follows the same licensing terms as the parent repository.

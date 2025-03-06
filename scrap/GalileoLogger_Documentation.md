# GalileoLogger Methods Documentation

The `GalileoLogger` class is a powerful tool for logging and tracking AI application traces in the Galileo platform. This document provides a comprehensive overview of all methods available in the `GalileoLogger` class, their parameters, and usage examples.

## Table of Contents

1. [Introduction](#introduction)
2. [Initialization](#initialization)
3. [Trace Management Methods](#trace-management-methods)
4. [Span Management Methods](#span-management-methods)
5. [Utility Methods](#utility-methods)
6. [Integration Wrappers](#integration-wrappers)
7. [Log Decorator](#log-decorator)
8. [Complete Usage Example](#complete-usage-example)

## Introduction

The `GalileoLogger` class extends the `TracesLogger` class and provides methods for creating, managing, and uploading traces to the Galileo platform. Traces represent complete interactions or workflows in your AI application, while spans represent individual steps within those traces (such as LLM calls, retrieval operations, or tool executions).

## Initialization

### Constructor

```python
def __init__(self, project: Optional[str] = None, log_stream: Optional[str] = None) -> None
```

Initializes a new GalileoLogger instance.

**Parameters:**
- `project` (Optional[str]): The name of the project to log traces to. If not provided, it will use the value from the `GALILEO_PROJECT` environment variable or a default value.
- `log_stream` (Optional[str]): The name of the log stream to log traces to. If not provided, it will use the value from the `GALILEO_LOG_STREAM` environment variable or a default value.

**Example:**
```python
from galileo import GalileoLogger

# Initialize with specific project and log stream
logger = GalileoLogger(project="my_project", log_stream="my_log_stream")

# Initialize using environment variables
logger = GalileoLogger()
```

## Trace Management Methods

### start_trace

```python
def start_trace(
    self,
    input: StepIOType,
    name: Optional[str] = None,
    duration_ns: Optional[int] = None,
    created_at: Optional[datetime] = None,
    metadata: Optional[dict[str, str]] = None,
    tags: Optional[list[str]] = None,
) -> Trace
```

Creates a new trace and adds it to the list of traces.

**Parameters:**
- `input` (StepIOType): Input to the trace.
- `name` (Optional[str]): Name of the trace.
- `duration_ns` (Optional[int]): Duration of the trace in nanoseconds.
- `created_at` (Optional[datetime]): Timestamp of the trace's creation.
- `metadata` (Optional[dict[str, str]]): Metadata associated with this trace.
- `tags` (Optional[list[str]]): Tags associated with this trace.

**Returns:**
- `Trace`: The created trace.

**Example:**
```python
trace = logger.start_trace(input="What's the weather in San Francisco?")
```

### add_single_llm_span_trace

```python
def add_single_llm_span_trace(
    self,
    input: LlmSpanAllowedInputType,
    output: LlmSpanAllowedOutputType,
    model: Optional[str],
    tools: Optional[list[dict]] = None,
    name: Optional[str] = None,
    created_at: Optional[datetime] = None,
    duration_ns: Optional[int] = None,
    metadata: Optional[dict[str, str]] = None,
    tags: Optional[list[str]] = None,
    num_input_tokens: Optional[int] = None,
    num_output_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    status_code: Optional[int] = None,
    time_to_first_token_ns: Optional[int] = None,
) -> Trace
```

Creates a new trace with a single LLM span and adds it to the list of traces.

**Parameters:**
- `input` (LlmSpanAllowedInputType): Input to the LLM.
- `output` (LlmSpanAllowedOutputType): Output from the LLM.
- `model` (Optional[str]): Model used for this span.
- `tools` (Optional[list[dict]]): List of available tools passed to LLM on invocation.
- `name` (Optional[str]): Name of the span.
- `duration_ns` (Optional[int]): Duration of the span in nanoseconds.
- `created_at` (Optional[datetime]): Timestamp of the span's creation.
- `metadata` (Optional[dict[str, str]]): Metadata associated with this span.
- `tags` (Optional[list[str]]): Tags associated with this span.
- `num_input_tokens` (Optional[int]): Number of input tokens.
- `num_output_tokens` (Optional[int]): Number of output tokens.
- `total_tokens` (Optional[int]): Total number of tokens.
- `temperature` (Optional[float]): Temperature used for generation.
- `status_code` (Optional[int]): Status code of the span execution.
- `time_to_first_token_ns` (Optional[int]): Time until the first token was returned.

**Returns:**
- `Trace`: The created trace.

**Example:**
```python
trace = logger.add_single_llm_span_trace(
    input="What's the weather in San Francisco?",
    output="The weather in San Francisco is currently sunny with a temperature of 72°F.",
    model="gpt-4o",
    num_input_tokens=10,
    num_output_tokens=20,
    total_tokens=30,
    duration_ns=1000000000  # 1 second in nanoseconds
)
```

## Span Management Methods

### add_llm_span

```python
def add_llm_span(
    self,
    input: LlmSpanAllowedInputType,
    output: LlmSpanAllowedOutputType,
    model: Optional[str],
    tools: Optional[list[dict]] = None,
    name: Optional[str] = None,
    created_at: Optional[datetime] = None,
    duration_ns: Optional[int] = None,
    metadata: Optional[dict[str, str]] = None,
    tags: Optional[list[str]] = None,
    num_input_tokens: Optional[int] = None,
    num_output_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    status_code: Optional[int] = None,
    time_to_first_token_ns: Optional[int] = None,
) -> LlmSpan
```

Adds a new LLM span to the current parent trace or workflow span.

**Parameters:**
- Same as `add_single_llm_span_trace`.

**Returns:**
- `LlmSpan`: The created span.

**Example:**
```python
trace = logger.start_trace(input="What's the weather in San Francisco?")
llm_span = logger.add_llm_span(
    input="What's the weather in San Francisco?",
    output="The weather in San Francisco is currently sunny with a temperature of 72°F.",
    model="gpt-4o",
    num_input_tokens=10,
    num_output_tokens=20,
    total_tokens=30,
    duration_ns=1000000000  # 1 second in nanoseconds
)
```

### add_retriever_span

```python
def add_retriever_span(
    self,
    input: str,
    output: RetrieverSpanAllowedOutputType,
    name: Optional[str] = None,
    duration_ns: Optional[int] = None,
    created_at: Optional[datetime] = None,
    metadata: Optional[dict[str, str]] = None,
    tags: Optional[list[str]] = None,
    status_code: Optional[int] = None,
) -> RetrieverSpan
```

Adds a new retriever span to the current parent trace or workflow span.

**Parameters:**
- `input` (str): Input to the retriever.
- `output` (RetrieverSpanAllowedOutputType): Documents retrieved from the retriever. Can be a string, list of strings, dictionary, list of dictionaries, Document object, or list of Document objects.
- `name` (Optional[str]): Name of the span.
- `duration_ns` (Optional[int]): Duration of the span in nanoseconds.
- `created_at` (Optional[datetime]): Timestamp of the span's creation.
- `metadata` (Optional[dict[str, str]]): Metadata associated with this span.
- `tags` (Optional[list[str]]): Tags associated with this span.
- `status_code` (Optional[int]): Status code of the span execution.

**Returns:**
- `RetrieverSpan`: The created span.

**Example:**
```python
trace = logger.start_trace(input="What's the weather in San Francisco?")
retriever_span = logger.add_retriever_span(
    input="What's the weather in San Francisco?",
    output=["The weather in San Francisco is currently sunny.", "The temperature is 72°F."],
    duration_ns=500000000  # 0.5 seconds in nanoseconds
)
```

### add_tool_span

```python
def add_tool_span(
    self,
    input: str,
    output: Optional[str] = None,
    name: Optional[str] = None,
    duration_ns: Optional[int] = None,
    created_at: Optional[datetime] = None,
    metadata: Optional[dict[str, str]] = None,
    tags: Optional[list[str]] = None,
    status_code: Optional[int] = None,
    tool_call_id: Optional[str] = None,
) -> ToolSpan
```

Adds a new tool span to the current parent trace or workflow span.

**Parameters:**
- `input` (str): Input to the tool.
- `output` (Optional[str]): Output from the tool.
- `name` (Optional[str]): Name of the span.
- `duration_ns` (Optional[int]): Duration of the span in nanoseconds.
- `created_at` (Optional[datetime]): Timestamp of the span's creation.
- `metadata` (Optional[dict[str, str]]): Metadata associated with this span.
- `tags` (Optional[list[str]]): Tags associated with this span.
- `status_code` (Optional[int]): Status code of the span execution.
- `tool_call_id` (Optional[str]): ID of the tool call.

**Returns:**
- `ToolSpan`: The created span.

**Example:**
```python
trace = logger.start_trace(input="What's the weather in San Francisco?")
tool_span = logger.add_tool_span(
    input="get_weather(location='San Francisco')",
    output="Sunny, 72°F",
    name="get_weather",
    duration_ns=200000000  # 0.2 seconds in nanoseconds
)
```

### add_workflow_span

```python
def add_workflow_span(
    self,
    input: str,
    output: Optional[str] = None,
    name: Optional[str] = None,
    duration_ns: Optional[int] = None,
    created_at: Optional[datetime] = None,
    metadata: Optional[dict[str, str]] = None,
    tags: Optional[list[str]] = None,
) -> WorkflowSpan
```

Adds a workflow span to the current parent trace or workflow span. This is useful for creating nested workflows.

**Parameters:**
- `input` (str): Input to the workflow.
- `output` (Optional[str]): Output from the workflow.
- `name` (Optional[str]): Name of the span.
- `duration_ns` (Optional[int]): Duration of the span in nanoseconds.
- `created_at` (Optional[datetime]): Timestamp of the span's creation.
- `metadata` (Optional[dict[str, str]]): Metadata associated with this span.
- `tags` (Optional[list[str]]): Tags associated with this span.

**Returns:**
- `WorkflowSpan`: The created span.

**Example:**
```python
trace = logger.start_trace(input="What's the weather in San Francisco?")
workflow_span = logger.add_workflow_span(
    input="Process weather query",
    name="weather_workflow",
)
# Add spans to the workflow
tool_span = logger.add_tool_span(
    input="get_weather(location='San Francisco')",
    output="Sunny, 72°F",
)
# Conclude the workflow
logger.conclude(output="Processed weather query")
```

### conclude

```python
def conclude(
    self,
    output: Optional[str] = None,
    duration_ns: Optional[int] = None,
    status_code: Optional[int] = None,
    conclude_all: bool = False,
) -> Optional[StepWithChildSpans]
```

Concludes the current trace or workflow span by setting the output of the current node.

**Parameters:**
- `output` (Optional[str]): Output of the node.
- `duration_ns` (Optional[int]): Duration of the node in nanoseconds.
- `status_code` (Optional[int]): Status code of the node execution.
- `conclude_all` (bool): If True, all spans will be concluded, including the current span. False by default.

**Returns:**
- `Optional[StepWithChildSpans]`: The parent of the current workflow. None if no parent exists.

**Example:**
```python
trace = logger.start_trace(input="What's the weather in San Francisco?")
llm_span = logger.add_llm_span(
    input="What's the weather in San Francisco?",
    output="The weather in San Francisco is currently sunny with a temperature of 72°F.",
    model="gpt-4o",
)
logger.conclude(output="The weather in San Francisco is currently sunny with a temperature of 72°F.")
```

## Utility Methods

### flush

```python
def flush(self) -> list[Trace]
```

Uploads all traces to Galileo.

**Returns:**
- `list[Trace]`: The list of uploaded traces.

**Example:**
```python
traces = logger.flush()
```

### async_flush

```python
async def async_flush(self) -> list[Trace]
```

Asynchronously uploads all traces to Galileo.

**Returns:**
- `list[Trace]`: The list of uploaded traces.

**Example:**
```python
import asyncio

async def main():
    traces = await logger.async_flush()

asyncio.run(main())
```

### terminate

```python
def terminate(self)
```

Terminates the logger and flushes all traces to Galileo. This method is automatically called when the Python interpreter exits.

**Example:**
```python
logger.terminate()
```

### current_parent

```python
def current_parent(self) -> Optional[StepWithChildSpans]
```

Returns the current parent trace or workflow span.

**Returns:**
- `Optional[StepWithChildSpans]`: The current parent trace or workflow span.

**Example:**
```python
parent = logger.current_parent()
```

## Integration Wrappers

Galileo provides several integration wrappers that automatically log interactions with popular AI libraries and frameworks. These wrappers make it easy to integrate Galileo logging into your existing applications with minimal code changes.

### OpenAI Wrapper

```python
from galileo.integrations.openai import openai
```

The OpenAI wrapper automatically logs all interactions with the OpenAI API, including chat completions, completions, and embeddings.

**Example:**
```python
from galileo.integrations.openai import openai
from galileo import GalileoLogger

# Initialize the logger
logger = GalileoLogger(project="my_project", log_stream="my_log_stream")

# Use the wrapped OpenAI client
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in San Francisco?"}]
)

# The interaction is automatically logged to Galileo
# No need to manually create spans or traces

# Flush the traces to Galileo
logger.flush()
```

### LangChain Wrapper

```python
from galileo.integrations.langchain import GalileoCallbackHandler
```

The LangChain wrapper logs all LangChain operations, including chains, agents, and retrievers.

**Example:**
```python
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from galileo.integrations.langchain import GalileoCallbackHandler
from galileo import GalileoLogger

# Initialize the logger
logger = GalileoLogger(project="my_project", log_stream="my_log_stream")

# Create a Galileo callback handler
handler = GalileoCallbackHandler()

# Create a LangChain chain
llm = OpenAI()
prompt = PromptTemplate.from_template("What's the weather in {location}?")
chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain with the Galileo callback handler
chain.run(location="San Francisco", callbacks=[handler])

# Flush the traces to Galileo
logger.flush()
```

### LlamaIndex Wrapper

```python
from galileo.integrations.llama_index import GalileoCallbackHandler
```

The LlamaIndex wrapper logs all LlamaIndex operations, including queries, retrievals, and indexing.

**Example:**
```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from galileo.integrations.llama_index import GalileoCallbackHandler
from galileo import GalileoLogger

# Initialize the logger
logger = GalileoLogger(project="my_project", log_stream="my_log_stream")

# Create a Galileo callback handler
callback_handler = GalileoCallbackHandler()

# Load documents and create an index
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Query the index with the Galileo callback handler
query_engine = index.as_query_engine(callback_manager=callback_handler)
response = query_engine.query("What's the weather in San Francisco?")

# Flush the traces to Galileo
logger.flush()
```

## Log Decorator

The `log` decorator is a convenient way to automatically log function calls as spans in Galileo. It can be applied to any function to track its execution and include it in the current trace.

```python
from galileo.decorators import log
```

### Usage

```python
@log(span_type="tool", name=None)
def your_function(arg1, arg2, ...):
    # Function implementation
    return result
```

**Parameters:**
- `span_type` (str): The type of span to create. Options include:
  - `"tool"`: For tool or function calls
  - `"llm"`: For language model interactions
  - `"retriever"`: For retrieval operations
  - `"workflow"`: For workflow steps
- `name` (Optional[str]): Custom name for the span. If not provided, the function name will be used.

**Example:**
```python
from galileo.decorators import log
from galileo import GalileoLogger

# Initialize the logger
logger = GalileoLogger(project="my_project", log_stream="my_log_stream")

# Start a trace
trace = logger.start_trace(input="What's 4 + seven?")

# Define a tool function with the log decorator
@log(span_type="tool")
def calculate(expression):
    try:
        result = eval(expression)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Call the function - it will be automatically logged
result = calculate("4 + 7")

# Conclude the trace
logger.conclude(output=f"The result is {result}")

# Flush the traces to Galileo
logger.flush()
```

In this example, the `calculate` function is automatically logged as a tool span in the current trace. The input to the span is the function arguments, and the output is the function return value.

### Nested Decorators

You can use the `log` decorator with other decorators. The order of decorators matters - the `log` decorator should typically be the outermost decorator to capture the full function execution:

```python
from galileo.decorators import log
import time

# Define a timing decorator
def timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.2f} seconds to run")
        return result
    return wrapper

# Apply both decorators - log should be outermost
@log(span_type="tool")
@timing_decorator
def process_data(data):
    # Process the data
    return processed_result
```

## Complete Usage Example

Here's a complete example demonstrating how to use the GalileoLogger class:

```python
from galileo import GalileoLogger
import time

# Initialize the logger
logger = GalileoLogger(project="my_project", log_stream="my_log_stream")

# Start a trace
trace = logger.start_trace(input="What's the weather in San Francisco?")

# Add a retriever span
start_time = time.time_ns()
# ... retrieval operation ...
end_time = time.time_ns()
retriever_span = logger.add_retriever_span(
    input="What's the weather in San Francisco?",
    output=["The weather in San Francisco is currently sunny.", "The temperature is 72°F."],
    duration_ns=end_time - start_time
)

# Add an LLM span
start_time = time.time_ns()
# ... LLM call ...
end_time = time.time_ns()
llm_span = logger.add_llm_span(
    input="What's the weather in San Francisco?",
    output="The weather in San Francisco is currently sunny with a temperature of 72°F.",
    model="gpt-4o",
    num_input_tokens=10,
    num_output_tokens=20,
    total_tokens=30,
    duration_ns=end_time - start_time
)

# Conclude the trace
logger.conclude(output="The weather in San Francisco is currently sunny with a temperature of 72°F.")

# Flush the traces to Galileo
logger.flush()
```

This example demonstrates a simple RAG (Retrieval-Augmented Generation) workflow where we first retrieve relevant documents and then use an LLM to generate a response based on those documents.

---

For more information, refer to the [Galileo documentation](https://docs.galileo.ai/). 
# Galileo OpenAI Integration Examples

This directory contains examples of how to use Galileo with OpenAI in two different ways:

## 1. Using the Galileo OpenAI Wrapper (app.py)

The `app.py` file demonstrates the simplest way to use Galileo with OpenAI by using the Galileo OpenAI wrapper:

```python
from galileo import openai  # The Galileo OpenAI client wrapper is all you need!

# Initialize the client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Make API calls as usual
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": prompt}],
)
```

With this approach, all OpenAI API calls are automatically logged to Galileo without any additional code. This is the simplest way to integrate Galileo into your application.

## 2. Using the Standard OpenAI Library with GalileoLogger (test.py)

The `test.py` file demonstrates how to use the standard OpenAI library directly while manually logging to Galileo using the `GalileoLogger` class:

```python
import openai  # Standard OpenAI library
from galileo import GalileoLogger  # Import GalileoLogger for logging

# Initialize the logger
logger = GalileoLogger(project="chatbot", log_stream="test")

# Initialize the standard OpenAI client
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Start a trace
trace = logger.start_trace(input=prompt)

# Record the start time
start_time = time.time_ns()

# Make the OpenAI API call directly
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": prompt}],
)

# Record the end time
end_time = time.time_ns()

# Log the LLM call as a span
logger.add_llm_span(
    input=prompt,
    output=response.choices[0].message.content.strip(),
    model="gpt-4o",
    duration_ns=end_time - start_time,
    num_input_tokens=response.usage.prompt_tokens,
    num_output_tokens=response.usage.completion_tokens,
    total_tokens=response.usage.total_tokens
)

# Conclude the trace
logger.conclude(output=response.choices[0].message.content.strip())

# Flush the traces to Galileo
logger.flush()
```

This approach gives you more control over what gets logged and when, allowing you to:

1. Create custom traces and spans
2. Add additional metadata to your traces
3. Log only specific API calls
4. Integrate with other parts of your application

## When to Use Each Approach

- **Use the Galileo OpenAI wrapper** when you want a simple drop-in replacement for the OpenAI library with automatic logging.
- **Use the standard OpenAI library with GalileoLogger** when you need more control over logging or want to integrate Galileo with other parts of your application.

## Running the Examples

To run the examples, you'll need to:

1. Install the required packages:
   ```
   pip install openai galileo python-dotenv
   ```

2. Set up your environment variables in a `.env` file:
   ```
    # Galileo Environment Variables
    GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
    GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
    GALILEO_LOG_STREAM=your-galileo-log-stream       # The name of the log stream you want to use for logging.
    
    # Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
    # GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo

   OPENAI_API_KEY=your_openai_api_key
   OPENAI_ORGANIZATION=your_openai_organization  # Optional
   ```

3. Run the examples:
   ```
   python app.py  # For the Galileo OpenAI wrapper example
   python test.py  # For the standard OpenAI library with GalileoLogger example
   ```

## Hallucination Demonstration

This project includes a demonstration of hallucinations in LLMs and techniques to prevent them.

### What are Hallucinations?

Hallucinations occur when an AI model generates factually incorrect information that is not grounded in any real-world knowledge. These are sometimes called "open-domain factual errors" and can significantly impact the reliability of your AI system.

### Running the Hallucination Demo

To run the hallucination demonstration:

```bash
python hallucination.py
```

This program will:

1. Ask a series of questions that might lead to hallucinations
2. Generate responses using different system prompts:
   - Unconstrained: No specific instructions about factual accuracy
   - Constrained: Explicit instructions to avoid speculation and guessing
   - RAG Simulation: Simulates a retrieval-augmented generation approach with a limited knowledge base

3. Use another LLM as a judge to evaluate whether hallucinations occurred in each response
4. Demonstrate solutions to prevent hallucinations:
   - Explicitly instructing the model to avoid guessing
   - Adding response validation
   - Using retrieval-augmented generation (RAG)
   - Implementing post-processing checks

### Metrics Used to Evaluate Hallucinations

The judge model evaluates responses on:
- Factual Accuracy: Whether statements are verifiably false
- Speculation: Whether speculation is presented as fact
- Uncertainty Handling: Whether uncertainty is appropriately expressed
- Citation Needs: Whether claims that should be cited are cited

Each response receives a hallucination score from 0-10, where 0 means no hallucination and 10 means completely hallucinated.

### Solutions to Prevent Hallucinations

1. **Explicitly Instruct the Model**: Add clear instructions in your system prompt to avoid guessing and speculation.
2. **Response Validation**: Implement automated validation using a judge model or other techniques.
3. **Retrieval-Augmented Generation (RAG)**: Ground responses in verified sources.
4. **Post-Processing Checks**: Run additional checks for factual accuracy before serving responses. 
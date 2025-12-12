# Galileo Distributed Tracing - Decorator Example

This example demonstrates distributed tracing across two services using Galileo's `@log` decorator.

## Architecture

- **Retrieval Service** (`retrieval_service.py`): A FastAPI service running on port 8000 that handles information retrieval
- **Orchestrator Service** (`main_run.py`): The main client that coordinates the RAG pipeline by calling the retrieval service

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# Navigate to the distributed_tracing_example directory
cd /path/to/distributed_tracing_example

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate 
```

### 2. Install Dependencies

This example uses a specific branch of the Galileo SDK with decorator support:
Change your requirements.txt -> replace `galileo[openai]` with this line
```
galileo[openai] @ git+https://github.com/rungalileo/galileo-python.git@adding_decorator_support
```
then run ->
```bash
pip install -r requirements.txt
```



### 3. Configure Environment Variables

Create a `.env` file in the **root `distributed_tracing_example` directory** (one level up from this folder):

```bash
# /path/to/distributed_tracing_example/.env

# Required: Your Galileo API key
GALILEO_API_KEY=your_api_key_here

# Required: OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Required: Enable streaming mode for distributed tracing
GALILEO_MODE=streaming

# Optional: Galileo project and log stream names
GALILEO_PROJECT=your_project_name
GALILEO_LOG_STREAM=decorator_example
```

### 4. Run the Services

You need to run both services in **separate terminal processes**.

#### Terminal 1: Start the Retrieval Service

```bash
# Make sure you're in the galileo-dt-decorator directory
cd /path/to/distributed_tracing_example/galileo-dt-decorator

# Activate venv (if not already activated)
source ../venv/bin/activate

# Start the retrieval service on port 8000
uvicorn retrieval_service:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Terminal 2: Run the Orchestrator

```bash
# In a NEW terminal, navigate to the galileo-dt-decorator directory
cd /path/to/distributed_tracing_example/galileo-dt-decorator

# Activate venv
source ../venv/bin/activate

# Run the orchestrator
python main_distributed_tracing.py
```

## Expected Output

When you run the orchestrator, you should see:

```
============================================================
Question: What did Galileo Galilei research?
============================================================
Answer: Galileo Galilei made scientific observations that transformed our understanding of the universe.
```
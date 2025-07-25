# Getting Started: Monitoring LangChain Agents with Galileo

This guide will walk you through setting up a Python project that uses [LangChain](https://python.langchain.com/) to build an AI agent, and [Galileo](https://www.rungalileo.io/) to monitor and log your agent's activity.
---

## 1. Prerequisites

- **Python 3.8+** installed on your system.
- A Galileo account and API key (see [Galileo docs](https://docs.rungalileo.io/) for how to get one).
- An OpenAI API key (for using OpenAI models with LangChain).

---

## 2. Install Required Packages

Open a terminal, create a virtual environment and install the required packages:

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- `langchain` and `langchain-openai` are for building and running the agent.
- `python-dotenv` is for loading environment variables (API keys).
- `galileo` is for Galileo monitoring.

---

## 3. Set Up Environment Variables

Copy the existing `.env.example` file, and rename it to `.env` in your project directory. 

```
GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
GALILEO_LOG_STREAM=your-galileo-log-stream       # The name of the log stream you want to use for logging.

# Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
# GALILEO_CONSOLE_URL=your-galileo-console-url

OPENAI_API_KEY=your-openai-api-key
```

- Replace `your-openai-api-key`, `your-galileo-project-name`, and `your-galileo-log-stream` with your actual values.
- If you are using a custom deployment of Galileo, set `GALILEO_CONSOLE_URL` to the URL of your Galileo deployment.
- This keeps your credentials secure and out of your code.

---

## 4. Create Your Agent Script

Create a file called `main.py` and add the following code:

```python
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from galileo import galileo_context
from galileo.handlers.langchain import GalileoCallback
import os

# 1. Load environment variables (API keys)
load_dotenv()

# 2. Define a simple tool for the agent to use
@tool
def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}! 👋"

# 3. Set up Galileo monitoring context
with galileo_context(project="langchain-docs", log_stream="my_log_stream"):
    # 4. Initialize the agent with the Galileo callback for monitoring
    agent = initialize_agent(
        tools=[greet],
        llm=ChatOpenAI(model="gpt-4", temperature=0.7, callbacks=[GalileoCallback()]),
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # 5. Run the agent and print the response
    if __name__ == "__main__":
        result = agent.invoke({"input": "Say hello to Erin"})
        print(f"\nAgent Response:\n{result}")
```

---

### Explanation of Each Step

1. **Load environment variables:**  
   This loads your API keys from the `.env` file so you don't have to hard-code them.

2. **Define a tool:**  
   Tools are functions your agent can use. Here, we define a simple `greet` tool.

3. **Set up Galileo context:**  
   The `galileo_context` context manager ensures all logs are tagged with your chosen project and log stream in Galileo.

4. **Initialize the agent:**  
   - The agent is set up with your tool, an OpenAI LLM, and the `GalileoCallback` for monitoring.
   - The callback automatically logs all agent activity to Galileo.

5. **Run the agent:**  
   - The agent is asked to "Say hello to Erin".
   - The response is printed to your terminal.

---

## 5. Run Your Script

In your terminal, run:

```sh
python main.py
```

You should see output like:

```
Agent Response:
Hello, Erin! 👋
```

---

## 6. View Logs in Galileo

- Log in to your Galileo dashboard.
- Navigate to the project (`langchain-docs`) and log stream (`my_log_stream`) you specified.
- You should see logs for your agent run, including:
  - The input prompt
  - The agent's reasoning steps
  - Tool usage
  - The final answer

---

## 7. Troubleshooting

- **No logs in Galileo?**
  - Double-check your API keys and project/log stream names.
  - Ensure your `.env` file is in the same directory as your script.
- **Errors about traces not being concluded?**
  - Make sure you are not using both the `@log` decorator and the `GalileoCallback` at the same time.
  - Only use the `GalileoCallback` for agent monitoring.

---

## 8. Customizing Your Agent

- **Add more tools:**  
  Define more functions with the `@tool` decorator and add them to the `tools` list.
- **Change the model:**  
  Use a different OpenAI model by changing the `model` parameter in `ChatOpenAI`.
- **Change the project/log stream:**  
  Update the values in `galileo_context` to organize your logs.

---

## 9. Best Practices & Tips

- **Use the Galileo context manager** to ensure logs are tagged correctly within the Galileo UI.
- **Use environment variables** for all secrets and API keys.

---

You now have a fully working, observable LangChain agent with Galileo monitoring!
If you want to add more features, track custom metrics, or troubleshoot, refer to the Galileo and LangChain documentation or reach out for support.

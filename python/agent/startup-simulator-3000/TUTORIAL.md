# 🎓 Tutorial: Building an AI-Powered Startup Pitch Generator

## Overview

### Learning Objectives

By the end of this tutorial, you will be able to:

* Build a complete AI agent system that coordinates multiple specialized tools using a custom framework
* Implement proper observability using Galileo logging with both tool spans and LLM spans
* Create a dual-mode AI application that generates both creative and professional startup pitches
* Develop a modern web interface for AI applications with real-time feedback
* Understand best practices for custom agent architecture, error handling, and deployment

### Intended Audience

This tutorial is designed for developers who want to learn how to build production-ready AI applications with proper observability using a custom agent framework. You should have:

* Basic knowledge of Python programming (intermediate level)
* Familiarity with async/await patterns in Python
* Understanding of web development concepts (HTML, CSS, JavaScript)
* Experience with API integrations and environment configuration

## 🚀 Getting Started

### Step 1: Environment Setup

First, make sure you have the prerequisites installed:

```bash
# Check Python version (should be 3.8+)
python --version

# Create and activate virtual environment

# Windows instructions: 
venv\Scripts\activate

# Mac instructions 
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: API Key Configuration

You'll need several API keys to run this application:

1. **OpenAI API Key** (Required)
   - Visit: https://platform.openai.com/api-keys
   - Create an account and generate a new API key
   - This is used for the AI language model

2. **NewsAPI Key** (Required for Serious Mode)
   - Visit: https://newsapi.org/register
   - Sign up for a free account
   - This provides business news for market analysis

3. **Galileo API Key** (Optional but Recommended)
   - Visit: https://console.galileo.ai/
   - Create an account and generate an API key
   - This provides observability and monitoring

### Step 3: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with your API keys
nano .env  # or use your preferred editor
```

Your `.env` file should look like this:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
NEWS_API_KEY=your-newsapi-key-here

# Galileo Observability (recommended)
GALILEO_API_KEY=your-galileo-api-key-here
GALILEO_PROJECT=startup-simulator-v1.2
GALILEO_LOG_STREAM=my_stream

# Optional Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
VERBOSITY=low
ENVIRONMENT=development
ENABLE_LOGGING=true
```

## 🏗️ Understanding the Architecture

### How the Application Works

The Startup Simulator 3000 follows this flow:

```
1. User Input → 2. Agent Planning → 3. Tool Execution → 4. Result Generation
```

#### Step 1: User Input
- User provides: Industry, Audience, Random Word
- System determines mode (Silly vs Serious)

#### Step 2: Agent Planning
- Custom AI agent analyzes the request
- Creates a step-by-step execution plan
- Selects appropriate tools based on mode

#### Step 3: Tool Execution
- **Silly Mode**: HackerNews Tool → Startup Simulator
- **Serious Mode**: NewsAPI Tool → Serious Startup Simulator
- Each tool executes with Galileo logging

#### Step 4: Result Generation
- Agent combines all results
- Formats the final startup pitch
- Returns structured output

### Core Components

#### 1. Flask Web Server (`app.py`)
```python
@app.route('/api/generate', methods=['POST'])
def generate_startup():
    # Handles web requests
    # Validates input
    # Calls the agent
    # Returns results
```

#### 2. Custom Agent Framework (`agent.py`)
```python
class SimpleAgent(Agent):
    def __init__(self, llm_provider, mode="silly"):
        # Initializes the agent with tools
        # Sets up Galileo logging
        # Configures execution mode
```

#### 3. Tools (`tools/`)
- `startup_simulator.py`: Generates creative pitches
- `serious_startup_simulator.py`: Generates professional plans
- `hackernews_tool.py`: Fetches tech trends
- `news_api_tool.py`: Fetches business news

#### 4. Web Interface (`templates/index.html`)
- 8-bit retro styling
- Mode selection
- Form validation
- Real-time feedback

## 🎯 Running the Application

### Option 1: Web Interface (Recommended)

```bash
# Start the Flask server
python app.py
```

Then open your browser to: **http://localhost:2021**

### Option 2: Command Line

```bash
# Run the CLI version
python run_startup_sim.py
```

### Option 3: Test Individual Tools

```bash
# Test the startup simulator directly
python -c "
import asyncio
from tools.startup_simulator import StartupSimulatorTool
result = asyncio.run(StartupSimulatorTool().execute('tech', 'developers', 'AI'))
print(result)
"
```

## 🔍 Understanding the Code

### Agent Execution Flow

Let's trace through what happens when you generate a startup pitch:

1. **Web Request** (`app.py`)
```python
@app.route('/api/generate', methods=['POST'])
def generate_startup():
    data = request.json
    industry = data.get('industry', '').strip()
    audience = data.get('audience', '').strip()
    random_word = data.get('randomWord', '').strip()
    mode = data.get('mode', 'silly').strip()
```

2. **Galileo Trace Start**
```python
logger = GalileoLogger(
    project=os.environ.get("GALILEO_PROJECT"),
    log_stream=os.environ.get("GALILEO_LOG_STREAM")
)
trace = logger.start_trace(f"Generate startup pitch - {mode} mode")
```

3. **Agent Creation**
```python
llm_provider = OpenAIProvider(config=LLMConfig(model="gpt-4", temperature=0.7))
agent = SimpleAgent(llm_provider=llm_provider, mode=mode)
```

4. **Task Execution**
```python
task = f"Generate a startup pitch for {industry} targeting {audience} with word '{random_word}'"
result = await agent.run(task, industry=industry, audience=audience, random_word=random_word)
```

### Tool Execution Example

Here's how the startup simulator tool works:

```python
class StartupSimulatorTool(BaseTool):
    async def execute(self, industry: str, audience: str, random_word: str, hn_context: str = "") -> str:
        # 1. Log inputs
        inputs = {"industry": industry, "audience": audience, "random_word": random_word}
        
        # 2. Create prompt
        prompt = f"Generate a creative startup pitch for {industry} targeting {audience}..."
        
        # 3. Call OpenAI API
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4"
        )
        
        # 4. Format output
        output = {
            "pitch": response.choices[0].message.content,
            "character_count": len(pitch),
            "timestamp": datetime.now().isoformat()
        }
        
        # 5. Log to Galileo
        logger.conclude(output=json.dumps(output), duration_ns=0)
        
        return json.dumps(output)
```

## 🎨 Customizing the Application

### Adding New Tools

To add a new tool, create a file in the `tools/` directory:

```python
# tools/my_new_tool.py
from agent_framework.tools.base import BaseTool
from agent_framework.models import ToolMetadata

class MyNewTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "my_new_tool"
        self.description = "Description of what this tool does"
    
    @classmethod
    def get_metadata(cls) -> ToolMetadata:
        return ToolMetadata(
            name="my_new_tool",
            description="Description of what this tool does",
            tags=["custom", "tool"],
            input_schema={
                "type": "object",
                "properties": {
                    "input_param": {"type": "string", "description": "Input parameter"}
                },
                "required": ["input_param"]
            },
            output_schema={
                "type": "string",
                "description": "Tool output"
            }
        )
    
    async def execute(self, input_param: str) -> str:
        # Your tool logic here
        result = f"Processed: {input_param}"
        return result
```

Then register it in the agent's tool registry in `agent.py`:

```python
def _register_tools(self) -> None:
    # Register your new tool
    self.tool_registry.register(
        metadata=MyNewTool.get_metadata(),
        implementation=MyNewTool
    )
```

### Modifying the Web Interface

The web interface is in `templates/index.html`. Key sections:

```html
<!-- Mode Selection -->
<div class="mode-selector">
    <button class="mode-btn" data-mode="silly">🎭 SILLY MODE</button>
    <button class="mode-btn" data-mode="serious">💼 SERIOUS MODE</button>
</div>

<!-- Input Form -->
<form id="startupForm">
    <input type="text" id="industry" placeholder="Industry (e.g., fintech)" required>
    <input type="text" id="audience" placeholder="Target Audience (e.g., millennials)" required>
    <input type="text" id="randomWord" placeholder="Random Word (e.g., blockchain)" required>
    <button type="submit">Generate Startup Pitch</button>
</form>
```

### Styling Changes

The CSS is in `static/css/style.css`. Key styling features:

```css
/* 8-bit Retro Theme */
body {
    background: linear-gradient(45deg, #1a1a2e, #16213e, #0f3460);
    font-family: 'Courier New', monospace;
    color: #00ff41;
}

/* Glowing Effects */
.glow {
    text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 30px #00ff41;
}

/* Animated Background */
@keyframes pixelate {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}
```

## 🔧 Debugging and Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. API Key errors
```bash
# Check your .env file
cat .env
# Make sure all required keys are set
```

#### 3. Galileo logging issues
```bash
# Galileo is optional - the app works without it
# Check your Galileo configuration
echo $GALILEO_API_KEY
echo $GALILEO_PROJECT
```

#### 4. Port conflicts
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=2022)  # Change 2021 to 2022
```

### Debug Mode

Enable debug logging by setting in `.env`:
```env
VERBOSITY=high
ENABLE_LOGGING=true
```

### Galileo Dashboard

If you have Galileo set up, you can view:
- Tool execution traces
- LLM call metrics
- Performance analytics
- Error tracking

Visit: https://console.galileo.ai/

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

For production, consider:

1. **Environment Variables**
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
```

2. **WSGI Server**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:2021 app:app
```

3. **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 2021
CMD ["python", "app.py"]
```

## 📚 Next Steps

### Learning Path

1. **Understand the Basics**
   - Read through `app.py` and understand the Flask routes
   - Study `agent.py` to understand the custom agent framework
   - Examine the tools in the `tools/` directory
   - Explore the `agent_framework/` directory to understand the architecture

2. **Experiment with Tools**
   - Try modifying the startup simulator prompts
   - Add new tools to the system
   - Test different LLM models

3. **Enhance the Interface**
   - Modify the CSS for different themes
   - Add new form fields
   - Implement real-time updates

4. **Scale the Application**
   - Add database storage for generated pitches
   - Implement user authentication
   - Add rate limiting and caching

### Advanced Topics

- **Custom Agent Development**: Learn more about building agent frameworks from scratch
- **Observability**: Deep dive into Galileo's monitoring capabilities
- **API Design**: Study RESTful API best practices
- **Frontend Development**: Explore modern JavaScript frameworks
- **Tool Architecture**: Understand how to design and implement custom tools

## 🎉 Congratulations!

You've successfully:
- Set up a complete AI application with a custom agent framework
- Understood the custom agentic architecture
- Implemented observability with Galileo
- Created a dual-mode startup pitch generator
- Built a modern web interface

You now have a solid foundation for building AI-powered applications with custom agent frameworks, proper observability, and user interfaces!

---

**Happy Coding! 🚀**

*This tutorial demonstrates building AI agents from scratch. For more information, explore the `agent_framework/` directory to understand the custom architecture.* 
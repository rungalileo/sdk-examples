# 🛠️ Installation Instructions

 et's get you up and running so you can start building awesome AI agents with Galileo!

## Prerequisites

Before we dive in, make sure you have:

- Python 3.8 or newer installed
- Basic terminal/command line experience
- API keys ready (or know how to get them)
- Git installed on your system

## Step 1: Clone the Repository

First, let's grab the code:

```bash
# Clone the repository
git clone https://github.com/[organization]/sdk-examples.git

# Navigate to the project folder
cd sdk-examples/python/agent/weather-vibes-agent
```

## Step 2: Set Up Your Environment

I recommend using `uv` for faster dependency management, but you can use standard Python tools if you prefer.

### Option A: Using UV (Recommended)

```bash
# Install UV if you don't have it
curl -sSf https://install.pypa.io/get-uv.py | python3 -

# Create a virtual environment
uv venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
uv install -r requirements.txt
```

### Option B: Using Standard Python Tools

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Get Your API Keys

You'll need four API keys to make the Weather Vibes Agent work:

### OpenAI API Key

1. Go to [OpenAI's platform](https://platform.openai.com/signup)
2. Create an account or sign in
3. Navigate to API Keys in your account settings
4. Click "Create new secret key"
5. Copy the key (you won't see it again!)

### WeatherAPI Key

1. Visit [WeatherAPI](https://www.weatherapi.com)
2. Create a free account
3. After logging in, go to "API Keys" tab
4. Copy your API key (or create a new one)
5. Note: It may take a few hours for a new key to activate

### YouTube Data API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the "YouTube Data API v3"
4. Create credentials for an API key
5. Copy your API key

### Galileo API Key

1. Sign up for a free account at [Galileo.ai](https://app.galileo.ai/sign-up)
2. Go to Settings → API Keys in the dashboard
3. Create a new API key
4. Copy your key

## Step 4: Configure Environment Variables

Create a `.env` file in the project root directory with your API keys:

```
# Galileo Environment Variables
GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
GALILEO_LOG_STREAM=weather_vibes_agent

# Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
# GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo

OPENAI_API_KEY=your_openai_key_here
WEATHERAPI_KEY=your_weatherapi_key_here
YOUTUBE_API_KEY=your_youtube_key_here
```

Replace `your_*_key_here` with your actual API keys.

## Step 5: Fix Import Paths (Important!)

The project may have import path issues. Let's fix them:

1. Open `agent/weather_vibes_agent.py` and check the import section. 
   If you see imports like:
   ```python
   from weather_vibes.tools.weather_tool import WeatherTool
   ```

2. Change them to:
   ```python
   from tools.weather_tool import WeatherTool
   from tools.recommendation_tool import RecommendationsTool
   from tools.youtube_tool import YouTubeTool
   from agent.descriptor import WEATHER_VIBES_DESCRIPTOR
   ```

3. Also update the project root path setting:
   ```python
   # Change this:
   project_root = current_dir.parent.parent
   
   # To this:
   project_root = current_dir.parent
   ```

## Step 6: Run the Agent

Now you're ready to run the Weather Vibes Agent:

```bash
# Basic usage
python agent.py "New York"

# Advanced usage
python agent.py --location "Tokyo" --units imperial --mood relaxing --verbose
```

This should show you weather information, recommendations, and a matching YouTube video!

## 🔍 Common Troubleshooting

### "ModuleNotFoundError: No module named 'weather_vibes'"

**Problem**: The agent is trying to import from a module that doesn't exist in the current structure.

**Solution**:
1. Follow the import fixes in Step 5 above
2. If issues persist, create a symbolic link:
   ```bash
   # From the project root directory:
   ln -s . weather_vibes
   ```

### "ModuleNotFoundError: No module named 'agent_framework'"

**Problem**: The Simple Agent Framework dependency is missing or not installed correctly.

**Solution**:
```bash
# Install the framework from GitHub
uv install git+https://github.com/rungalileo/simple-agent-framework.git@main

# Or with pip
pip install git+https://github.com/rungalileo/simple-agent-framework.git@main
```

### API Key Errors

**Problem**: "Invalid API key", "API key not found", or similar errors.

**Solutions**:
- Double-check your `.env` file for typos
- Make sure your `.env` file is in the correct location (project root)
- For WeatherAPI: New API keys may take a few hours to activate
- For YouTube: Ensure the API is enabled in Google Cloud Console
- For OpenAI: Check your account has billing set up

### "KeyError" or Missing Fields in Response

**Problem**: The agent crashes when trying to access data from API responses.

**Solution**: The APIs occasionally change their response format or return partial data.
```python
# Add defensive checks in your code:
weather_condition = weather_result.get("condition", "unknown")
```

### Template Not Found Errors

**Problem**: Jinja template errors mentioning that templates can't be found.

**Solution**: Make sure the templates directory exists and contains the required template files:
```bash
# Check the templates directory
ls -la templates

# Create a basic system template if missing
mkdir -p templates
echo "You are a helpful weather agent. Help the user based on their request." > templates/system.j2
```

### Rate Limit Errors

**Problem**: "Rate limit exceeded" errors from any of the APIs.

**Solutions**:
- OpenAI: Wait a minute and try again, or upgrade your plan
- YouTube: Create a new API key with higher quotas
- WeatherAPI: Upgrade to a paid plan for more requests

### SSL Certificate Errors

**Problem**: SSL/TLS certificate verification failures when making API requests.

**Solution**: Update your CA certificates or adjust the request settings:
```bash
# Update certificates (MacOS)
open /Applications/Python\ 3.x/Install\ Certificates.command

# Update certificates (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install ca-certificates
```

### "No module named 'dotenv'"

**Problem**: The python-dotenv package is missing.

**Solution**:
```bash
uv install python-dotenv
# or
pip install python-dotenv
```

## Still Having Issues?

Here are a few more advanced troubleshooting steps:

1. **Debug Mode**: Run the agent in debug mode to see more detailed logs:
   ```bash
   # Set logging level to DEBUG
   export PYTHONPATH=.
   python -m agent --debug "New York"
   ```

2. **Check Python Version**: Ensure you're using Python 3.8 or newer:
   ```bash
   python --version
   ```

3. **Clean Install**: If all else fails, try a completely fresh installation:
   ```bash
   # Remove the virtual environment
   rm -rf venv
   
   # Create a new one
   uv venv venv
   source venv/bin/activate
   
   # Install all dependencies fresh
   uv install -r requirements.txt
   ```

4. **Update Dependencies**: Sometimes updating dependencies can fix compatibility issues:
   ```bash
   uv install -U -r requirements.txt
   ```

In the next section, we'll dive into how to use Galileo to monitor and improve your agent. Stay tuned!

~ Erin

# 🌦️ Weather Vibes Agent Cookbook

A comprehensive tutorial for building a weather-based recommendation agent with Galileo observability.

## Overview

This cookbook will guide you through building, understanding, and monitoring the Weather Vibes Agent - an AI agent that combines weather data, recommendations, and video suggestions, all monitored using Galileo.ai's observability platform.

**What you'll build:** A command-line agent that:
1. Fetches current weather for any location
2. Generates item recommendations based on the weather
3. Finds YouTube videos matching the weather mood
4. Captures detailed traces and metrics for analysis

**What you'll learn:**
- Building multi-service AI agents
- Integrating with external APIs
- Instrumenting code with Galileo
- Implementing proper error handling
- Analyzing agent performance

## Prerequisites

- Python 3.8+
- API keys for:
  - OpenAI
  - WeatherAPI
  - YouTube Data API
  - Galileo
- Basic Python knowledge
- Terminal/command-line familiarity

## Environment Setup

**Ingredients:**
- git
- Python environment tools
- Package manager (pip or uv)

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/[organization]/sdk-examples.git
   cd sdk-examples/python/agent/weather-vibes-agent
   ```

2. **Create a virtual environment:**
  
  ```bash
   # Using standard venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # OR using uv (faster)
   uv venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # OR using uv
   uv install -r requirements.txt
   ```

4. **Create a .env file** in the project root:
   ```
   OPENAI_API_KEY=your_openai_key_here
   WeatherAPI_KEY=your_weatherapi_key_here
   YOUTUBE_API_KEY=your_youtube_key_here
   GALILEO_API_KEY=your_galileo_key_here
   GALILEO_LOG_STREAM=weather_vibes_agent
   ```

## Understanding the Agent Architecture

The Weather Vibes Agent consists of several key components:

### 🧠 Agent Core (`agent/weather_vibes_agent.py`)
Handles the main agent logic, coordinates tools, and processes requests.

### 🛠️ Tools
Specialized modules for specific tasks:
- **Weather Tool (`tools/weather_tool.py`)**: Fetches weather data from WeatherAPI.com
- **Recommendations Tool (`tools/recommendation_tool.py`)**: Generates weather-appropriate item suggestions
- **YouTube Tool (`tools/youtube_tool.py`)**: Finds videos matching the weather mood

### 📝 Descriptor (`descriptor.py`)
Defines the agent's capabilities, inputs, outputs, and configuration.

### 🔍 Instrumentation (`agent.py`)
Wraps the agent with Galileo monitoring for observability.

### 📑 Templates (`templates/`)
Contains Jinja templates for generating system prompts.

## Recipe 3: The Weather Tool

Let's examine the Weather Tool to understand how it works and where Galileo fits in.

**Key Ingredients:**
- WeatherAPI.com
- Async HTTP requests
- Error handling
- Response parsing

**How it works:**

1. **API Integration:**
   The tool makes requests to the WeatherAPI.com to get current weather data.

2. **Request Formatting:**
   ```python
   url = "http://api.weatherapi.com/v1/forecast.json"
   params = {
       "key": api_key,
       "q": location,
       "days": days,
       "aqi": "yes",
       "alerts": "yes"
   }
   ```

3. **Response Processing:**
   The tool extracts and formats relevant information from the API response:
   ```python
   current = data["current"]
   location_data = data["location"]
   
   return {
       "location": location_data["name"],
       "region": location_data["region"],
       "country": location_data["country"],
       "temperature_c": current["temp_c"],
       "temperature_f": current["temp_f"],
       "condition": current["condition"]["text"],
       "condition_icon": current["condition"]["icon"],
       "humidity": current["humidity"],
       "wind_kph": current["wind_kph"],
       "wind_mph": current["wind_mph"],
       "wind_direction": current["wind_dir"],
       "feels_like_c": current["feelslike_c"],
       "feels_like_f": current["feelslike_f"],
       "is_day": current["is_day"] == 1,
   }
   ```

4. **Error Handling:**
   The tool includes robust error handling to gracefully manage API failures.

**Where Galileo Comes In:**
The tool itself doesn't directly use Galileo. Instead, the main `agent.py` wraps the tool execution with Galileo's `@log` decorator:

```python
@log(span_type="tool", name="weather_tool")
async def get_weather(weather_tool, location, days=1):
    """Get weather data with Galileo tracing"""
    result = await weather_tool.execute(location=location, days=days)
    return result
```

This creates a span in Galileo that:
- Captures the input location and days parameter
- Records the tool's output
- Measures execution time
- Tracks any errors

## Recipe 4: The Recommendations Tool

This tool generates clothing and item recommendations based on weather conditions.

**Key Ingredients:**
- OpenAI API
- Weather condition mapping
- JSON response parsing

**How it works:**

1. **Prompt Engineering:**
   The tool constructs a prompt for the LLM using the weather data:
   ```python
   prompt = (
       f"Based on the following weather conditions:\n"
       f"Location: {weather['location']}\n"
       f"Temperature: {weather['temperature_c']}°C ({weather['temperature_f']}°F)\n"
       f"Condition: {weather['condition']}\n"
       f"Humidity: {weather['humidity']}%\n"
       f"Wind Speed: {weather['wind_kph']} km/h ({weather['wind_mph']} mph)\n\n"
       f"Recommend {max_items} items a person should bring or wear. "
       f"Return just a simple list of items, no explanations."
   )
   ```

2. **LLM Integration:**
   The tool calls OpenAI's API to generate recommendations:
   ```python
   response = await self.client.chat.completions.create(
       model=self.model,
       messages=[{"role": "user", "content": prompt}],
       temperature=0.7,
       max_tokens=150
   )
   ```

3. **Response Parsing:**
   The tool processes the LLM's response to extract a clean list of recommendations.

**Galileo Integration:**
Similar to the Weather Tool, recommendations are traced with:

```python
@log(span_type="tool", name="recommendations_tool")
async def get_recommendations(recommendations_tool, weather, max_items=5):
    """Get recommendations with Galileo tracing"""
    result = await recommendations_tool.execute(weather=weather, max_items=max_items)
    return result
```

This allows you to analyze:
- How different weather inputs affect recommendations
- LLM response quality
- Processing time

## Recipe 5: The YouTube Tool

This tool finds videos that match the current weather condition or mood.

**Key Ingredients:**
- YouTube Data API
- Weather-to-mood mapping
- Search query construction

**How it works:**

1. **Mood Mapping:**
   The tool maps weather conditions to appropriate moods:
   ```python
   WEATHER_MOOD_MAP = {
       "Clear": ["sunny", "bright", "cheerful"],
       "Clouds": ["relaxing", "chill", "ambient"],
       "Rain": ["rainy", "cozy", "relaxing"],
       "Drizzle": ["light rain", "peaceful", "gentle"],
       "Thunderstorm": ["dramatic", "intense", "powerful"],
       "Snow": ["winter", "snowfall", "peaceful"],
       "Mist": ["foggy", "mysterious", "calm"],
       "Fog": ["atmospheric", "misty", "moody"],
   }
   ```

2. **Query Construction:**
   The tool builds a YouTube search query:
   ```python
   query = f"{mood} music {weather_condition.lower()} weather"
   ```

3. **API Integration:**
   The tool searches YouTube and selects an appropriate video.

**Galileo Integration:**
Like the other tools, YouTube searches are traced with:

```python
@log(span_type="tool", name="youtube_tool")
async def find_weather_video(youtube_tool, weather_condition, mood_override=None):
    """Find YouTube videos with Galileo tracing"""
    result = await youtube_tool.execute(
        weather_condition=weather_condition,
        mood_override=mood_override
    )
    return result
```

This helps you monitor:
- YouTube API success rate
- Query effectiveness
- Response times

## Recipe 6: Main Agent Workflow

The main workflow in `agent.py` ties everything together and adds Galileo instrumentation.

**Key Ingredients:**
- Galileo context
- Logging decorators
- Workflow spans
- Error handling

**How it works:**

1. **Setting Up the Context:**
   ```python
   with galileo_context(log_stream=galileo_log_stream):
       # Agent execution happens here
   ```

2. **Creating the Main Span:**
   ```python
   @log(span_type="entrypoint", name="weather_vibes_agent")
   async def run_agent_with_inputs(location, units, mood, recommendations, verbose):
       # Agent execution logic
   ```

3. **Creating the Workflow Span:**
   ```python
   @log(span_type="workflow", name="weather_vibes_workflow")
   async def process_request(agent, request):
       # Core workflow logic
   ```

4. **Tool Execution:**
   Each tool call is wrapped with its own span.

5. **Result Aggregation:**
   Results from all tools are combined into a single response.

**Galileo's Role:**
Galileo creates a hierarchical trace structure:
- The entrypoint span contains the entire run
- The workflow span tracks the main agent logic
- Individual tool spans track specific operations
- Metadata captures important context

This lets you analyze the complete flow and identify bottlenecks or errors.

## Recipe 7: Running the Agent

Now that you understand how it all works, let's run the agent!

**Steps:**

1. **Basic Usage:**
   ```bash
   python agent.py "New York"
   ```

2. **Advanced Options:**
   ```bash
   python agent.py --location "Tokyo" --units imperial --mood relaxing --verbose
   ```

3. **Expected Output:**
   You should see:
   - Weather information for the specified location
   - Recommendations based on the weather
   - A YouTube video matching the weather mood
   - Confirmation that Galileo traces have been collected

## Recipe 8: Viewing Traces in Galileo

Now it's time to see the results of our instrumentation in Galileo!

**Steps:**

1. **Log into Galileo:**
   Visit [app.galileo.ai](https://app.galileo.ai) and log in.

2. **View Your Traces:**
   - Navigate to the Traces section
   - Look for the `weather_vibes_agent` log stream
   - Click on a recent trace

3. **Explore the Hierarchy:**
   You'll see a visualization showing:
   - The main entrypoint span
   - The workflow span
   - Individual tool spans

4. **Analyze Performance:**
   In the trace view, you can:
   - See the execution time for each component
   - View the input and output data
   - Identify any errors or warnings
   - Compare multiple runs

5. **Identify Optimization Opportunities:**
   Look for:
   - Slow API calls
   - Bottlenecks in the workflow
   - Error patterns
   - Response quality issues

## Recipe 9: Common Issues and Solutions

Here are some problems you might encounter and how to fix them:

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'weather_vibes'`

**Solution:**
- Fix the imports in `agent/weather_vibes_agent.py`
- Or create a symbolic link: `ln -s . weather_vibes`

### API Key Issues

**Problem:** "Invalid API key" errors

**Solution:**
- Double-check your `.env` file
- For WeatherAPI.com, make sure you have signed up and confirmed your email
- For YouTube, ensure the API is enabled in Google Cloud Console

### Template Issues

**Problem:** Jinja template errors

**Solution:**
```bash
mkdir -p templates
echo "You are a helpful weather agent." > templates/system.j2
```

### Galileo Connection Issues

**Problem:** Traces aren't showing up in Galileo

**Solution:**
- Confirm your API key is valid
- Check internet connectivity
- Ensure `flush()` is being called at the end of execution

## Recipe 10: Extending the Agent

Want to make the Weather Vibes Agent even better? Here are some ideas:

### Add New Tools

Create a new tool file in the `tools/` directory:
```python
class ForecastTool:
    async def execute(self, location, days=5):
        # Implement 5-day forecast logic
        pass
```

### Add More Instrumentation

Add custom metrics to your Galileo spans:
```python
@log(span_type="tool", name="forecast_tool", metrics={"days_requested": days})
async def get_forecast(forecast_tool, location, days=5):
    result = await forecast_tool.execute(location=location, days=days)
    return result
```

### Implement Caching

Add caching to improve performance:
```python
class WeatherTool:
    def __init__(self):
        self.cache = {}
        
    async def execute(self, location, units="metric"):
        cache_key = f"{location}_{units}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        # Normal API call logic
        self.cache[cache_key] = result
        return result
```

## Conclusion

You've now learned how to build, run, and monitor the Weather Vibes Agent with Galileo! 

**Key Takeaways:**
- Multi-tool agents can combine various APIs into a unified experience
- Proper error handling and modular design make agents more robust
- Galileo observability provides valuable insights into agent performance
- Well-structured tracing helps identify issues and optimization opportunities

**Next Steps:**
- Try adding new features to the agent
- Experiment with different tracing approaches
- Analyze your traces to identify performance improvements
- Apply these patterns to your own AI applications

Happy building! 
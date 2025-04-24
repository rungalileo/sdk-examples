#!/usr/bin/env python
"""
Galileo-instrumented Weather Vibes Agent.
Adds tracing and logging for performance evaluation and debugging.

Usage:
    python galileo_agent.py [location]
    python galileo_agent.py -l "Tokyo" -u imperial -m relaxing
"""
import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from galileo import log, galileo_context

# Load environment variables & set up path
load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Quick environment check
required_keys = ["OPENAI_API_KEY", "OPENWEATHER_API_KEY", "YOUTUBE_API_KEY", "GALILEO_API_KEY"]
if any(not os.getenv(key) for key in required_keys):
    missing = [key for key in required_keys if not os.getenv(key)]
    print(f"Missing API keys: {', '.join(missing)}")
    print("Add them to your .env file or environment variables")
    sys.exit(1)

# Check for Galileo log stream
galileo_log_stream = os.getenv("GALILEO_LOG_STREAM")
if not galileo_log_stream:
    print("Warning: GALILEO_LOG_STREAM environment variable not set.")
    print("Using default log stream name.")
    galileo_log_stream = "weather_vibes_agent"

# Import the agent
from agent.weather_vibes_agent import WeatherVibesAgent

# Tool wrappers with Galileo instrumentation
@log(span_type="tool", name="weather_tool")
async def get_weather(weather_tool, location, units="metric"):
    """Get weather data with Galileo tracing"""
    result = await weather_tool.execute(location=location, units=units)
    return result

@log(span_type="tool", name="recommendations_tool")
async def get_recommendations(recommendations_tool, weather, max_items=5):
    """Get recommendations with Galileo tracing"""
    result = await recommendations_tool.execute(weather=weather, max_items=max_items)
    return result

@log(span_type="tool", name="youtube_tool")
async def find_weather_video(youtube_tool, weather_condition, mood_override=None):
    """Find YouTube videos with Galileo tracing"""
    result = await youtube_tool.execute(
        weather_condition=weather_condition,
        mood_override=mood_override
    )
    return result

@log(span_type="workflow", name="weather_vibes_workflow")
async def process_request(agent, request):
    """Main workflow with Galileo tracing"""
    try:
        # Extract request data
        input_data = request.get("input", {})
        config = request.get("config", {})
        metadata = request.get("metadata", {})
        
        # Parse parameters
        location = input_data.get("location")
        units = input_data.get("units", "metric")
        verbose = config.get("verbose", False)
        max_recommendations = config.get("max_recommendations", 5)
        video_mood = config.get("video_mood")
        
        # Validate location
        if not location:
            return {"error": 400, "message": "Location is required"}
        
        # Update search history
        if not hasattr(agent.state, "search_history"):
            agent.state.search_history = []
            
        if location not in agent.state.search_history:
            agent.state.search_history.append(location)
            if len(agent.state.search_history) > 5:
                agent.state.search_history = agent.state.search_history[-5:]
        
        # Execute tools
        weather_result = await get_weather(agent.weather_tool, location, units)
        if "error" in weather_result:
            return {"error": 500, "message": f"Weather API error: {weather_result['message']}"}
        
        recommendations = await get_recommendations(
            agent.recommendations_tool, weather_result, max_recommendations
        )
        
        video_result = await find_weather_video(
            agent.youtube_tool, weather_result["condition"], video_mood
        )
        
        # Prepare response
        result = {
            "weather": weather_result,
            "recommendations": recommendations,
            "video": video_result
        }
        
        # Filter weather details if not verbose
        if not verbose and "weather" in result:
            result["weather"] = {
                "location": weather_result["location"],
                "temperature": weather_result["temperature"],
                "condition": weather_result["condition"],
                "humidity": weather_result["humidity"],
                "wind_speed": weather_result["wind_speed"]
            }
        
        # Build final response
        response = {"output": result}
        if "agent_id" in request:
            response["agent_id"] = request["agent_id"]
        if metadata:
            response["metadata"] = metadata
        
        return response
        
    except Exception as e:
        return {"error": 500, "message": f"Error: {str(e)}"}

# Simple wrapper for logging the inputs
@log(span_type="entrypoint", name="weather_vibes_agent")
async def run_agent_with_inputs(location, units, mood, recommendations, verbose):
    """Run the agent with specific inputs logged via the decorator"""
    print(f"Getting weather for: {location} (with Galileo tracing)")
    
    # Create agent and request
    agent = WeatherVibesAgent()
    request = {
        "input": {"location": location, "units": units},
        "config": {
            "verbose": verbose,
            "max_recommendations": recommendations,
            "video_mood": mood
        },
        "metadata": {
            "user_id": "demo_user", 
            "session_id": "demo_session",
            "galileo_instrumented": True
        }
    }
    
    try:
        # Process request
        response = await process_request(agent, request)
        
        # Display results
        if "error" in response:
            print(f"\n❌ Error: {response['message']}")
            return
            
        output = response["output"]
        weather = output["weather"]
        temp_unit = "°F" if units == "imperial" else "°C"
        speed_unit = "mph" if units == "imperial" else "m/s"
        
        # Display weather
        print(f"\n🌤️  WEATHER FOR {weather['location']} 🌤️")
        print(f"• Temperature: {weather['temperature']}{temp_unit}")
        print(f"• Condition: {weather['condition']}")
        print(f"• Humidity: {weather['humidity']}%")
        print(f"• Wind Speed: {weather['wind_speed']} {speed_unit}")
        
        if verbose and "feels_like" in weather:
            print(f"• Feels Like: {weather['feels_like']}{temp_unit}")
            print(f"• Description: {weather.get('description', '')}")
        
        # Display recommendations
        print(f"\n🧳 RECOMMENDATIONS:")
        for item in output["recommendations"]:
            print(f"• {item}")
        
        # Display video
        video = output["video"]
        print(f"\n🎵 MATCHING VIDEO:")
        if "error" in video:
            print(f"• Couldn't find a video: {video.get('error')}")
        else:
            print(f"• {video['title']}")
            print(f"• By: {video['channel']}")
            print(f"• URL: {video['url']}")
        
        print("\n📊 Galileo traces have been collected for this run")
        print("View them in your Galileo dashboard")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

# Entry point function
async def main():
    """Main entry point that uses galileo_context to set up the trace environment"""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Run the Galileo-instrumented Weather Vibes Agent")
    parser.add_argument("location", nargs="?", help="Location (e.g., 'Tokyo')")
    parser.add_argument("-l", "--location", dest="location_alt", help="Alternative location specification")
    parser.add_argument("-u", "--units", choices=["metric", "imperial"], default="metric", help="Units (metric/imperial)")
    parser.add_argument("-m", "--mood", help="Video mood (e.g., 'relaxing', 'upbeat')")
    parser.add_argument("-r", "--recommendations", type=int, default=5, help="Number of recommendations")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed weather info")
    args = parser.parse_args()
    
    # Get location
    location = args.location or args.location_alt
    if not location:
        location = input("Enter location (default: New York): ") or "New York"
    
    # Use galileo_context with the log stream from environment
    with galileo_context(log_stream=galileo_log_stream):
        # Create a dictionary of inputs as metadata
        input_data = {
            "location": location,
            "units": args.units,
            "mood": args.mood,
            "recommendations": args.recommendations,
            "verbose": args.verbose
        }
        
        # Run the agent with the wrapped function to log inputs
        await run_agent_with_inputs(
            location=location,
            units=args.units,
            mood=args.mood,
            recommendations=args.recommendations,
            verbose=args.verbose
        )

if __name__ == "__main__":
    asyncio.run(main()) 
"""
Weather Vibes Agent Package
"""

# Import the main agent class for easy access
try:
    from agent.weather_vibes_agent import WeatherVibesAgent
except ImportError:
    pass  # Handle the case if the module isn't ready yet

# Import tools for easy access
try:
    from tools.weather_tool import WeatherTool
    from tools.recommendation_tool import RecommendationsTool
    from tools.youtube_tool import YouTubeTool
except ImportError:
    pass  # Handle the case if the tools aren't ready yet

# Define what's available from this package
__all__ = ["WeatherVibesAgent", "WeatherTool", "RecommendationsTool", "YouTubeTool"]

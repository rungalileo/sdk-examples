"""
Weather Vibes Agent package
"""

from .weather_vibes_agent import WeatherVibesAgent

__all__ = ["WeatherVibesAgent"]

# Make the descriptor easily importable
try:
    from .descriptor import WEATHER_VIBES_DESCRIPTOR
except ImportError:
    pass  # Handle the case if the file doesn't exist yet

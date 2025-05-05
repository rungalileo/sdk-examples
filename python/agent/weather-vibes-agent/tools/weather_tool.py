"""
Weather tool for fetching current weather conditions using WeatherAPI.com.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel
from agent_framework.tools.base import BaseTool
import requests


class WeatherInput(BaseModel):
    """Input schema for the weather tool"""

    location: str
    days: int = 1


class WeatherTool(BaseTool):
    """Tool for fetching weather information"""

    name = "get_weather"
    description = "Get the current weather conditions for a location"
    tags = ["weather", "utility"]
    input_schema = WeatherInput.model_json_schema()

    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY")
        if not self.api_key:
            raise ValueError("WeatherAPI.com API key not found in environment")
        self.base_url = "http://api.weatherapi.com/v1/forecast.json"

    async def execute(self, location: str, days: int = 1) -> Dict[str, Any]:
        """
        Execute the tool to get current weather and forecast.

        Args:
            location: The location to get weather for (city name, zip code, lat/long, etc.)
            days: Number of days of forecast to include (1-7)

        Returns:
            Dictionary containing weather information
        """
        params = {
            "key": self.api_key,
            "q": location,
            "days": days,
            "aqi": "yes",  # Include air quality data
            "alerts": "yes"  # Include weather alerts
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract relevant weather information
            current = data["current"]
            location_data = data["location"]
            
            weather_info = {
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
            
            # Add forecast information if requested
            if days > 1 and "forecast" in data:
                forecast_days = []
                for day in data["forecast"]["forecastday"]:
                    forecast_days.append({
                        "date": day["date"],
                        "max_temp_c": day["day"]["maxtemp_c"],
                        "min_temp_c": day["day"]["mintemp_c"],
                        "condition": day["day"]["condition"]["text"],
                        "chance_of_rain": day["day"]["daily_chance_of_rain"],
                    })
                weather_info["forecast"] = forecast_days
            
            # Add alerts if available
            if "alerts" in data and data["alerts"].get("alert"):
                weather_info["alerts"] = data["alerts"]["alert"]

            return weather_info
        except Exception as e:
            return {
                "error": str(e),
                "message": f"Failed to get weather for location: {location}",
            }

"""
Tool for generating item recommendations based on weather conditions.
"""

from typing import Dict, Any, List
from pydantic import BaseModel
from agent_framework.tools.base import BaseTool


class RecommendationsInput(BaseModel):
    """Input schema for recommendations tool"""

    weather: Dict[str, Any]
    max_items: int = 5


class RecommendationsTool(BaseTool):
    """Tool for generating weather-based recommendations"""

    name = "get_recommendations"
    description = "Get recommendations for items to bring based on weather conditions"
    tags = ["weather", "recommendations"]
    input_schema = RecommendationsInput.model_json_schema()

    async def execute(self, weather: Dict[str, Any], max_items: int = 5) -> List[str]:
        """
        Execute the tool to get recommendations.

        Args:
            weather: Weather information dictionary
            max_items: Maximum number of recommendations to provide

        Returns:
            List of recommended items
        """
        recommendations = []

        # Basic recommendation logic based on weather conditions
        condition = weather.get("condition", "").lower()
        # Use temperature_c as primary, with fallback to other temperature fields
        temp = weather.get("temperature_c", 
               weather.get("temp_c", 
               weather.get("temperature", 0)))

        # Rain-related recommendations
        if any(x in condition.lower() for x in ["rain", "drizzle", "shower", "precipitation", "wet"]):
            recommendations.extend(["☔ Umbrella", "🧥 Raincoat"])

        # Sun-related recommendations
        if any(x in condition.lower() for x in ["clear", "sun", "sunny"]):
            recommendations.extend(["🕶️ Sunglasses", "🧴 Sunscreen", "🧢 Cap"])

        # Cloud-related recommendations
        if any(x in condition.lower() for x in ["cloud", "overcast", "fog", "mist"]):
            recommendations.extend(["🔦 Flashlight", "📸 Camera"])

        # Snow-related recommendations
        if any(x in condition.lower() for x in ["snow", "blizzard", "sleet", "ice"]):
            recommendations.extend(["❄️ Snow boots", "🧤 Gloves", "⛄ Snow gear"])

        # Temperature-based recommendations
        if temp < 5:  # Cold
            recommendations.extend(["🧣 Scarf", "🧥 Heavy coat", "🔥 Hand warmers"])
        elif temp < 15:  # Cool
            recommendations.extend(["👖 Jeans", "🧦 Warm socks", "🧥 Light jacket"])
        elif temp < 25:  # Warm
            recommendations.extend(["👕 T-shirt", "🩳 Shorts", "🧴 Sunscreen"])
        else:  # Hot
            recommendations.extend(["👙 Swimwear", "🌴 Water bottle", "🩴 Sandals"])

        # Wind-related recommendations
        wind_speed = weather.get("wind_kph", weather.get("wind_mph", weather.get("wind_speed", 0)))
        if wind_speed > 20:
            recommendations.extend(["🌬️ Windbreaker", "🪁 Hat with strap"])

        # Humidity-based recommendations
        humidity = weather.get("humidity", 0)
        if humidity > 70:
            recommendations.append("💦 Moisture-wicking clothes")
        
        # Check for air quality if available
        if "air_quality" in weather and isinstance(weather["air_quality"], dict):
            aqi = weather["air_quality"].get("us-epa-index", 0)
            if aqi > 3:  # Moderate or worse air quality
                recommendations.append("😷 Face mask")

        # Return unique recommendations, limited to max_items
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:max_items]

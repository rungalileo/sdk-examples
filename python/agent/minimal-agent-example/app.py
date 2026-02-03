import os
import streamlit as st
from galileo import (
    log,
    galileo_context,
    openai,
)
from pydantic import BaseModel
import json
from typing import Callable
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


class DestinationOverviewRequest(BaseModel):
    destination: str


class ItineraryRequest(BaseModel):
    destination: str
    days: int


class WeatherRequest(BaseModel):
    destination: str


class BudgetRequest(BaseModel):
    destination: str
    days: int


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get the weather forecast for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia",
                    },
                },
                "required": [
                    "destination",
                ],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "estimate_travel_budget",
            "description": "Estimate the travel budget for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for the itinerary",
                    },
                },
                "required": ["destination", "days"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_destination_overview",
            "description": "Generate a destination overview.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia",
                    },
                },
                "required": [
                    "destination",
                ],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_itinerary",
            "description": "Generate a travel itinerary for a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "City and country e.g. Bogotá, Colombia",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days for the itinerary",
                    },
                },
                "required": ["destination", "days"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]


# =============================================================================
# Local function to simulate an API call for weather data.
# =============================================================================
@log(span_type="tool")
def get_weather_forecast(destination: str) -> str:
    # Simulate a local function call that returns dummy weather data.
    return f"Weather forecast for {destination}: Mostly sunny with a slight chance of rain."


# =============================================================================
# LLM call: Generate a destination overview.
# =============================================================================
def generate_destination_overview(destination: str) -> str:
    prompt = f"Provide a brief overview of {destination}, including its top attractions, " "cultural highlights, and essential travel tips."
    # Call the OpenAI API (assuming proper API key configuration)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    # Extract and return the text from the response.
    return response.choices[0].message.content.strip()


# =============================================================================
# LLM call: Generate a day-by-day travel itinerary.
# =============================================================================
def generate_itinerary(destination: str, days: int) -> str:
    prompt = f"""
Plan a {days}-day travel itinerary for a trip to {destination}. 
Include daily sightseeing activities, dining suggestions, and local experiences.

Important:
- Every plan must contain a destination overview and an itinerary.
- Only include a travel budget and weather info if the user requests it.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


# =============================================================================
# LLM call: Estimate a travel budget.
# =============================================================================
def estimate_travel_budget(destination: str, days: int, itinerary: str | None = None) -> str:
    itinerary_prompt = f"\n\nHere is the itinerary:\n\n {itinerary}" if itinerary else ""
    prompt = (
        f"Estimate a travel budget for a {days}-day trip to {destination} that covers accommodation, "
        "food, transportation, and activities. Provide a rough breakdown of the costs (in USD)."
        f"{itinerary_prompt}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


# =============================================================================
# LLM call: Decide which functions to call and assemble the itinerary.
# =============================================================================
@log
def assemble_travel_plan(query: str, info_callback: Callable[[str], None]) -> str:
    #
    # Develop a plan
    #

    function_calling_prompt = f"""
You are an expert travel planner. I've included a request that you need to process:

\"{query}\"

Important:
- Every plan MUST contain a destination overview and an itinerary. Make sure to always call the `generate_destination_overview` and `generate_itinerary` functions.
- Only include a travel budget (using the `estimate_travel_budget` function) and weather info (using the `get_weather_forecast` function) if the user requests it.
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": function_calling_prompt}],
        tools=tools,
    )

    # Extract function call responses
    message_response = response.choices[0].message

    if message_response.function_call:
        function_calls = [message_response.function_call]  # Single function case
    else:
        function_calls = message_response.tool_calls or []  # Multiple function calls

    destination_overview = ""
    itinerary = ""
    budget = ""
    weather = ""

    #
    # Process multiple function calls
    #
    for function_call in function_calls:
        function_name = function_call.function.name
        function_args = json.loads(function_call.function.arguments)

        if function_name == "generate_destination_overview":
            destination_overview_request = DestinationOverviewRequest(**function_args)
            info_callback(f"Generating a destination overview for {destination_overview_request.destination}...")
            destination_overview = destination_overview + "\n" + generate_destination_overview(destination_overview_request.destination)

        elif function_name == "generate_itinerary":
            itinerary_request = ItineraryRequest(**function_args)
            info_callback(f"Generating an itinerary for {itinerary_request.destination}...")
            itinerary = itinerary + "\n" + generate_itinerary(itinerary_request.destination, itinerary_request.days)

        elif function_name == "estimate_travel_budget":
            budget_request = BudgetRequest(**function_args)
            info_callback(f"Generating a travel budget for {budget_request.destination}...")
            budget = (
                budget
                + "\n"
                + estimate_travel_budget(
                    destination=budget_request.destination,
                    days=budget_request.days,
                    itinerary=itinerary,
                )
            )

        elif function_name == "get_weather_forecast":
            weather_request = WeatherRequest(**function_args)
            info_callback(f"Generating a weather forecast for {weather_request.destination}...")
            weather = weather + "\n" + get_weather_forecast(weather_request.destination)

    #
    # Assemble the results
    #
    info_callback("Assembling the final plan...")
    travel_budget = f"Travel budget: {budget}" if budget else ""
    weather_forecast = f"Weather forecast: {weather}" if weather else ""
    assembly_prompt = f"""
You are an expert travel planner.

My original request was: \"{query}\"

You have generated the following outputs:

Destination overview: {destination_overview}
Itinerary: {itinerary}
""" + travel_budget + weather_forecast + f"\n\nPlease package the information above into a plan that I can use for my next trip."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": assembly_prompt}],
    )
    return response.choices[0].message.content.strip()


# =============================================================================
# Main Streamlit App
# =============================================================================
def main():
    st.title("Travel Itinerary Planner")
    st.write("Plan your next adventure with our AI-powered travel planner.")

    with st.container():
        # User inputs for the travel query.
        query = st.text_input(
            "Where would you like to go?",
            "Rome for 5 days later this month, please include a trip budget and weather info",
        )

        # Create a button for planning the trip.
        plan_trip_clicked = st.button("Plan My Trip")

        info_placeholder = st.empty()

        # Create an empty container for results so that previous outputs are cleared on re-run.
        result_container = st.empty()

        def info_callback(message):
            info_placeholder.info(message)

        if plan_trip_clicked:
            if not query.strip():
                info_placeholder.warning("Please enter a travel query.")
            else:
                result_container.empty()
                info_placeholder.info("Generating your travel plan. Please wait...")

                with galileo_context():
                    plan = assemble_travel_plan(query, info_callback)

                # Clear the info message once the generation is complete.
                info_placeholder.empty()

                with result_container.container():
                    st.write(plan)


if __name__ == "__main__":
    main()

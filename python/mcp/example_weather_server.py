from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for a location.
    
    Args:
        location: The city or location to get weather for (e.g., "New York", "Paris")
        
    Returns:
        A string describing the current weather conditions
        
    Examples:
        To get weather for London, provide location="London"
    """
    print(f"Weather requested for: {location}")  # Add logging
    return f"It's always sunny in {location}"

if __name__ == "__main__":
    print("Starting weather server on http://localhost:8000/sse")
    mcp.run(transport="sse")

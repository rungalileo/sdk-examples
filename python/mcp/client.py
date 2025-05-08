# client.py
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    print("Starting client...")
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",  # Executable
        args=["server.py"],  # Path to your server script
        env=None,  # Optional environment variables
    )

    print(f"Connecting to server using: python server.py")
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            print("Connected to server via stdio")
            async with ClientSession(read, write) as session:
                # Initialize the connection
                print("Initializing session...")
                init_response = await session.initialize()
                print("Session initialized")
                print("\n=== INITIALIZATION RESPONSE ===")
                print(json.dumps(init_response.model_dump(), indent=2))
                
                # List available tools
                print("\n=== LISTING TOOLS ===")
                tools_response = await session.list_tools()
                print("Available tools:", [tool.name for tool in tools_response.tools])
                print("\n=== TOOLS RESPONSE ===")
                print(json.dumps(tools_response.model_dump(), indent=2))
                
                # Call the add tool
                print("\n=== CALLING ADD TOOL ===")
                call_result = await session.call_tool("add", arguments={"a": 5, "b": 3})
                print(f"Result of add(5, 3): {call_result}")
                # The call_result is often not a Pydantic model, so we need to handle it differently
                print("\n=== TOOL CALL RESPONSE ===")
                if hasattr(call_result, "model_dump"):
                    print(json.dumps(call_result.model_dump(), indent=2))
                else:
                    # Try to extract more details from the response
                    print("Raw response type:", type(call_result))
                    print("Response details:", call_result)
                    
                # List available resources
                print("\n=== LISTING RESOURCES ===")
                resources_response = await session.list_resources()
                print("Available resources:", [resource.template for resource in resources_response.resources])
                print("\n=== RESOURCES RESPONSE ===")
                print(json.dumps(resources_response.model_dump(), indent=2))
                
                # Access the greeting resource
                print("\n=== ACCESSING GREETING RESOURCE ===")
                greeting_content, mime_type = await session.read_resource("greeting://Alice")
                print(f"Greeting: {greeting_content}")
                print(f"MIME type: {mime_type}")
                # Resource responses might not be Pydantic models
                print("\n=== RESOURCE RESPONSE DETAILS ===")
                print("Content type:", type(greeting_content))
                print("MIME type details:", mime_type)
                
                if hasattr(greeting_content, "model_dump"):
                    print(json.dumps(greeting_content.model_dump(), indent=2))
                if hasattr(mime_type, "model_dump"):
                    print(json.dumps(mime_type.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nClient terminated by user")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()

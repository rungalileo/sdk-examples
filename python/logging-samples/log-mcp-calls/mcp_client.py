"""
An MCP Client implementation to connect to an MCP server and manage tools.
"""

import os

from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """MCP Client to connect to MCP server and manage tools"""

    def __init__(self):
        # Initialize session and client objects
        self._session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()
        self.tools = []

    async def connect_to_server(self):
        """Connect to an MCP server"""
        # Establish streamable HTTP connection
        read, write, _ = await self._exit_stack.enter_async_context(
            streamablehttp_client(
                url=os.environ.get(
                    "MCP_SERVER_URL", "https://api.galileo.ai/mcp/http/mcp"
                ),
                headers={
                    "Galileo-API-Key": os.environ["GALILEO_API_KEY"],
                    "Accept": "text/event-stream",
                },
            )
        )

        # Create the MCP client session
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        # Initialize the session
        await self._session.initialize()

        # List the available tools
        response = await self._session.list_tools()
        self.tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]
        print(
            "\nConnected to server with tools:",
            [tool["name"] for tool in self.tools],
        )

    async def call_tool(self, tool_name: str, input_data: dict):
        """Call a tool by name with the provided input data"""
        # Ensure a session is established
        if not self._session:
            raise RuntimeError("MCP Client is not connected to a server.")

        # Call the tool and return the result
        return await self._session.call_tool(tool_name, input_data)

    async def cleanup(self):
        """Clean up resources"""
        await self._exit_stack.aclose()

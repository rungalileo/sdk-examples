# MCP Server and Client Demo

This example demonstrates a basic Model Context Protocol (MCP) server and client implementation using the Python SDK.

## Overview

The Model Context Protocol (MCP) is a standardized way for AI models to interact with external tools and data sources. This demo includes:

- A simple MCP server with an `add` tool and a `greeting` resource
- A client that connects to the server and demonstrates each capability
- Detailed output showing the raw MCP messages

## Prerequisites

- Python 3.12 (Python 3.13 may cause numpy-related installation issues)
- pipenv (this project uses pipenv instead of uv)

## Setup

1. Clone this repository
2. Install dependencies
3. To run the client: `python client.py`
4. To run the server and access the Inspector, run `mcp dev server.py` and then open `http://127.0.0.1:6274/#tools` in the browser.
5. In the Inspector, you can connect to the server using `transport` = `STDIO`, `command`=`mcp`, `arguments`=`run server.py`. You should be able to list and experiment with the tools as shown ![image](https://github.com/user-attachments/assets/a07dc542-9982-4667-b943-f3a0daa19cb4)

## Sample Output

```
Starting client...
Connecting to server using: python server.py
Connected to server via stdio
Initializing session...
Session initialized

=== INITIALIZATION RESPONSE ===
{
  "meta": null,
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "experimental": {},
    "logging": null,
    "prompts": {
      "listChanged": false
    },
    "resources": {
      "subscribe": false,
      "listChanged": false
    },
    "tools": {
      "listChanged": false
    }
  },
  "serverInfo": {
    "name": "Demo",
    "version": "1.6.0"
  },
  "instructions": null
}

=== LISTING TOOLS ===
[04/06/25 12:15:27] INFO     Processing request of type ListToolsRequest                                                                            server.py:534
Available tools: ['add']

=== TOOLS RESPONSE ===
{
  "meta": null,
  "nextCursor": null,
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers",
      "inputSchema": {
        "properties": {
          "a": {
            "title": "A",
            "type": "integer"
          },
          "b": {
            "title": "B",
            "type": "integer"
          }
        },
        "required": [
          "a",
          "b"
        ],
        "title": "addArguments",
        "type": "object"
      }
    }
  ]
}

=== CALLING ADD TOOL ===
                    INFO     Processing request of type CallToolRequest                                                                             server.py:534
Result of add(5, 3): meta=None content=[TextContent(type='text', text='8', annotations=None)] isError=False

=== TOOL CALL RESPONSE ===
{
  "meta": null,
  "content": [
    {
      "type": "text",
      "text": "8",
      "annotations": null
    }
  ],
  "isError": false
}

=== LISTING RESOURCES ===
                    INFO     Processing request of type ListResourcesRequest                                                                        server.py:534
Available resources: []

=== RESOURCES RESPONSE ===
{
  "meta": null,
  "nextCursor": null,
  "resources": []
}

=== ACCESSING GREETING RESOURCE ===
                    INFO     Processing request of type ReadResourceRequest                                                                         server.py:534
Greeting: ('meta', None)
MIME type: ('contents', [TextResourceContents(uri=AnyUrl('greeting://Alice'), mimeType='text/plain', text='Hello, Alice!')])

=== RESOURCE RESPONSE DETAILS ===
Content type: <class 'tuple'>
MIME type details: ('contents', [TextResourceContents(uri=AnyUrl('greeting://Alice'), mimeType='text/plain', text='Hello, Alice!')])
```
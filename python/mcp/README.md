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

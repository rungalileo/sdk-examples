import nest_asyncio
nest_asyncio.apply()
import os
import asyncio
import streamlit as st
from typing import Annotated, Dict, List, Any, Tuple

from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool, Tool, tool
from langchain_core.messages import AIMessage, HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langgraph.prebuilt import ToolNode, tools_condition


def create_standalone_tool_wrapper(tool_name, tool_description, math_server_path, weather_server_path):
    """Create a wrapper that makes a fresh client for each tool call."""
    
    def sync_func(*args, **kwargs):
        # Handle input arguments
        input_dict = {}
        if args and len(args) == 1 and isinstance(args[0], dict):
            input_dict = args[0].copy()
        else:
            input_dict = kwargs.copy()
        
        # Map __arg1 parameter if needed
        if '__arg1' in input_dict:
            if tool_name == "add" or tool_name == "multiply":
                try:
                    input_dict['a'] = int(input_dict.pop('__arg1'))
                except ValueError:
                    return f"Error: '{input_dict['__arg1']}' is not a valid number for parameter 'a'"
            elif tool_name == "get_weather":
                input_dict['location'] = input_dict.pop('__arg1')
        
        # Create a fresh event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_tool():
                # Create a completely new client
                client = MultiServerMCPClient(
                    {
                        "math": {
                            "command": "python",
                            "args": [math_server_path],
                            "transport": "stdio",
                        },
                        "weather": {
                            "url": "http://localhost:8000/sse",
                            "transport": "sse",
                        }
                    }
                )
                
                try:
                    # Start the client
                    await client.__aenter__()
                    
                    # Get tools from this fresh client
                    tools = client.get_tools()
                    
                    # Find the matching tool
                    for tool in tools:
                        if tool.name == tool_name:
                            # Execute the tool
                            result = await tool.ainvoke(input=input_dict)
                            return result
                    
                    return f"Tool {tool_name} not found"
                finally:
                    # Don't try to close the client - just let it go out of scope
                    # This avoids the "cancel scope in different task" error
                    pass
            
            return loop.run_until_complete(run_tool())
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
        finally:
            loop.close()
    
    return Tool(
        name=tool_name,
        description=tool_description,
        func=sync_func
    )


def create_async_to_sync_wrapper(async_tool: BaseTool) -> BaseTool:
    """Create a synchronous wrapper for an async tool."""
    
    def sync_func(*args, **kwargs):
        # Handle input arguments
        input_dict = {}
        if args and len(args) == 1 and isinstance(args[0], dict):
            input_dict = args[0].copy()
        else:
            input_dict = kwargs.copy()
        
        # Map __arg1 to the first parameter if needed
        if '__arg1' in input_dict and hasattr(async_tool, 'args_schema'):
            schema = async_tool.args_schema.schema()
            if 'properties' in schema and schema['properties']:
                first_param = next(iter(schema['properties'].keys()))
                input_dict[first_param] = input_dict.pop('__arg1')
        
        # Create a fresh event loop for each call
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(async_tool.ainvoke(input=input_dict))
        except Exception as e:
            return f"Error executing {async_tool.name}: {str(e)}"
        finally:
            loop.close()
    
    return Tool(
        name=async_tool.name,
        description=async_tool.description,
        func=sync_func
    )


async def setup_mcp(math_server_path: str, weather_server_path: str):
    """Set up MCP client and tools."""
    # Create a client that will be stored in the session
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": [math_server_path],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    )
    
    # Enter the context manager to start the servers
    await client.__aenter__()
    
    # Get the tools
    async_mcp_tools = client.get_tools()
    
    return client, async_mcp_tools


def initialize_agent():
    """Initialize the agent with all tools."""
    @tool
    def human_assistance(query: str) -> str:
        """Request assistance from a human."""
        st.session_state.waiting_for_human = True
        st.session_state.human_query = query
        return "Waiting for human response..."

    # Path to your MCP servers
    math_server_path = "/Users/sid/Desktop/galileo/sdk-examples/python/mcp/example_math_server.py"
    weather_server_path = "/Users/sid/Desktop/galileo/sdk-examples/python/mcp/example_weather_server.py"

    # Create a temporary MCP client to get tool definitions - run async in sync context
    loop = asyncio.new_event_loop()
    try:
        client, async_mcp_tools = loop.run_until_complete(
            setup_mcp(math_server_path, weather_server_path)
        )
        
        # Create wrapper tools that preserve the original schemas
        mcp_tools = []
        for async_tool in async_mcp_tools:
            # Get the args schema
            schema = None
            if hasattr(async_tool, 'args_schema'):
                # Check if args_schema is already a dict or has a schema() method
                if isinstance(async_tool.args_schema, dict):
                    schema = async_tool.args_schema
                elif hasattr(async_tool.args_schema, 'schema'):
                    schema = async_tool.args_schema.schema()
            
            # Create a tool wrapper that preserves the schema
            tool_wrapper = create_schema_preserving_wrapper(
                async_tool.name,
                async_tool.description,
                schema,
                math_server_path,
                weather_server_path
            )
            mcp_tools.append(tool_wrapper)
    finally:
        loop.close()
    
    # Combine all tools
    tavily_tool = TavilySearch(max_results=2)
    all_tools = [tavily_tool, human_assistance] + mcp_tools
    
    # Create the agent
    graph, config = create_agent(all_tools)
    
    return graph, all_tools, config

def create_schema_preserving_wrapper(tool_name, tool_description, args_schema, math_server_path, weather_server_path):
    """Create a wrapper that preserves the original schema from the MCP tool."""
    
    def sync_func(*args, **kwargs):
        # Handle both positional and keyword arguments
        input_dict = {}
        
        # If called with a dictionary as first positional argument
        if args and len(args) == 1 and isinstance(args[0], dict):
            input_dict = args[0].copy()
        # If called with keyword arguments (like location="New York")
        else:
            input_dict = kwargs.copy()
            
        # Debug logging
        print(f"Tool {tool_name} called with: {input_dict}")
            
        # Create a fresh event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            async def run_tool():
                # Create a new client
                client = None
                try:
                    client = MultiServerMCPClient({
                        "math": {
                            "command": "python",
                            "args": [math_server_path],
                            "transport": "stdio",
                        },
                        "weather": {
                            "url": "http://localhost:8000/sse",
                            "transport": "sse",
                        }
                    })
                    
                    # Start the client
                    await client.__aenter__()
                    
                    # Get tools
                    tools = client.get_tools()
                    
                    # Find matching tool
                    for tool in tools:
                        if tool.name == tool_name:
                            # Execute the tool
                            result = await tool.ainvoke(input=input_dict)
                            return result
                    return f"Tool {tool_name} not found"
                except Exception as e:
                    print(f"Error in async execution: {e}")
                    return f"Error: {str(e)}"
                finally:
                    # Properly close the client if it was created
                    if client is not None:
                        try:
                            await client.__aexit__(None, None, None)
                        except Exception as e:
                            print(f"Error closing client: {e}")
            
            # Use a timeout to prevent hanging
            return loop.run_until_complete(asyncio.wait_for(run_tool(), timeout=10.0))
        except asyncio.TimeoutError:
            return f"Error: Tool {tool_name} execution timed out"
        except Exception as e:
            print(f"Error in sync wrapper: {e}")
            return f"Error executing {tool_name}: {str(e)}"
        finally:
            # Clean up pending tasks
            pending_tasks = asyncio.all_tasks(loop)
            for task in pending_tasks:
                task.cancel()
            
            # Run the event loop a bit more to process cancellations
            try:
                loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
            except Exception:
                pass
                
            # Finally close the loop
            loop.close()
    
    # Use StructuredTool with the original schema
    if args_schema:
        from langchain_core.tools import StructuredTool
        # Use from_function instead of direct constructor
        return StructuredTool.from_function(
            func=sync_func,
            name=tool_name,
            description=tool_description,
            args_schema=args_schema
        )
    else:
        from langchain_core.tools import Tool
        return Tool(
            name=tool_name,
            description=tool_description,
            func=sync_func
        )


def create_agent(tools: List[BaseTool]) -> Tuple[Any, Dict]:
    """Create the LangGraph agent with the specified tools."""
    # Define the state type
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    # Initialize graph builder
    graph_builder = StateGraph(State)
    memory = MemorySaver()

    # Initialize LLM
    llm = init_chat_model("openai:gpt-4.1-mini")
    llm_with_tools = llm.bind_tools(tools)

    # Define chatbot node
    def chatbot(state: State):
        message = llm_with_tools.invoke(state["messages"])
        return {"messages": [message]}

    graph_builder.add_node("chatbot", chatbot)

    # Set up tool node
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    # Set up graph edges
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    # Compile the graph
    graph = graph_builder.compile(checkpointer=memory)
    config = {"configurable": {"thread_id": "1"}}
    
    return graph, config


def handle_human_assistance():
    """Handle the case when the agent is waiting for human assistance."""
    with st.chat_message("assistant"):
        st.write(f"I need your help with: {st.session_state.human_query}")
    
    human_response = st.chat_input("Provide your response to the assistant...")
    if human_response:
        # Resume the agent with the human response
        human_command = Command(resume={"data": human_response})
        
        # Process agent response
        events = st.session_state.agent.stream(
            human_command,
            st.session_state.config,
            stream_mode="values",
        )
        
        # Process the response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            for event in events:
                if "messages" in event:
                    ai_message = event["messages"][-1]
                    response_placeholder.write(ai_message.content)
                    # Store the message
                    st.session_state.messages.append(ai_message)
        
        # Reset waiting state
        st.session_state.waiting_for_human = False
        st.session_state.human_query = None
        
        # Force a rerun to update the UI
        st.rerun()


def handle_user_input():
    """Handle normal user input and agent response."""
    user_input = st.chat_input("Ask the AI assistant...")
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append(HumanMessage(content=user_input))
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Process agent response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Stream the response
            events = st.session_state.agent.stream(
                {"messages": [HumanMessage(content=user_input)]},
                st.session_state.config,
                stream_mode="values",
            )
            
            for event in events:
                if "messages" in event:
                    ai_message = event["messages"][-1]
                    response_placeholder.write(ai_message.content)
                    # Store the message
                    st.session_state.messages.append(ai_message)
            
            # Check if we hit an interrupt
            snapshot = st.session_state.agent.get_state(st.session_state.config)
            
            if snapshot.next and snapshot.next[0] == "tools":
                # Check if we're waiting for human assistance
                for msg in reversed(snapshot.values["messages"]):
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            if tool_call["name"] == "human_assistance":
                                st.session_state.waiting_for_human = True
                                st.session_state.human_query = tool_call["args"]["query"]
                                break
                
                # If waiting for human input, force a rerun to show the input form
                if st.session_state.waiting_for_human:
                    st.rerun()


def display_chat_history():
    """Display all messages in the chat history."""
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
                # Display tool calls if present
                if hasattr(message, "tool_calls") and message.tool_calls:
                    with st.expander("Tool calls"):
                        for tool_call in message.tool_calls:
                            st.code(f"Tool: {tool_call['name']}\nArgs: {tool_call['args']}")


def main():
    """Main function for the Streamlit app."""
    # Set up environment variables
    os.environ["GALILEO_PROJECT"] = "demo-simple-agent-langgraph"
    os.environ["GALILEO_LOG_STREAM"] = "dev"
    os.environ["LANGCHAIN_PROJECT"] = "galileo-demo-simple-agent-langgraph"

    # Streamlit app title
    st.title("LangGraph AI Agent")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.agent_initialized = False
        st.session_state.waiting_for_human = False
        st.session_state.human_query = None

    # Initialize the agent if not already done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing AI agent..."):
            st.session_state.agent, st.session_state.tools, st.session_state.config = initialize_agent()
            st.session_state.agent_initialized = True

    # Display chat history
    display_chat_history()

    # Handle waiting for human input or normal user input
    if st.session_state.waiting_for_human:
        handle_human_assistance()
    else:
        handle_user_input()


if __name__ == "__main__":
    main()

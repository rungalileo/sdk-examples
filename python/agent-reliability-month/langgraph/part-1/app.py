import os
import streamlit as st
from dotenv import load_dotenv
from typing import Annotated, Dict, List, Any, Tuple

from typing_extensions import TypedDict

from galileo.handlers.langchain import GalileoCallback
from galileo import galileo_context

from langchain_tavily import TavilySearch
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import check_supplier_compliance, assess_disruption_risk

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


def create_agent(tools: List[BaseTool], callbacks: List) -> Tuple[Any, Dict]:
    """Create the LangGraph agent with the specified tools."""

    # Initialize graph builder
    graph_builder = StateGraph(State)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4", callbacks=callbacks)
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
    graph = graph_builder.compile()
    config = {"configurable": {"thread_id": "1"}}
    
    return graph, config

def display_chat_history():
    """Display all messages in the chat history."""
    if not st.session_state.messages:
        return
        
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
        else:
            print("!!!!!! OTHER MESSAGE TYPE:")
            print(message)



def main(session_name="Custom session name"):
    """Main function for the Streamlit app."""

    # Streamlit app title
    st.title("LangGraph AI Agent")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    # Initialize the agent if not already done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing AI agent..."):
            galileo_context.start_session(name=session_name)
            galileo_context.start_session(name=session_name)

            tavily_tool = TavilySearch(max_results=2)
            all_tools = [tavily_tool, assess_disruption_risk, check_supplier_compliance]
            # Create the agent
            st.session_state.agent, st.session_state.config = create_agent(
                all_tools, callbacks=[GalileoCallback()]
            )
            st.session_state.tools = all_tools
            st.session_state.agent_initialized = True

    # Display chat history
    display_chat_history()

    # Add chat input
    user_input = st.chat_input("Type your message here...")
    
    # Process user input when submitted
    if user_input:
        # Add user message to chat history
        user_message = HumanMessage(content=user_input)
        st.session_state.messages.append(user_message)
        
        # Display the user message immediately
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response from agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run the agent with the user message
                result = st.session_state.agent.invoke(
                    {"messages": user_message},
                    config=st.session_state.config
                )
                
                # Get the latest AI message
                ai_message = result["messages"][-1]
                st.session_state.messages.append(ai_message)
                st.write(ai_message.content)


if __name__ == "__main__":
    os.environ["GALILEO_PROJECT"] = "langgraph-demo1-test"
    os.environ["GALILEO_LOG_STREAM"] = "dev"
    main(session_name="Test Chat- 4 turn: v2")

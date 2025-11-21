import os
import dotenv
from agent import create_agent
from traceloop.sdk import Traceloop
from langchain_core.messages import HumanMessage

dotenv.load_dotenv()

Traceloop.init(
    app_name="LangGraph-Traceloop-Demo",
    disable_batch=False,  # Enable batching for better performance
    resource_attributes={
        "service.version": "1.0.0",
        "deployment.environment": "development",
    },
)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING TOOL-BASED AGENT")
    print("="*60)
    
    # Create the agent
    app = create_agent()
    
    # Prepare the input with instructions for the agent
    user_question = "what moons did galileo discover"
    
    # Create a message that instructs the agent to use the tools
    instructions = f"""Please help me answer this question: "{user_question}"

To do this, follow these steps:
1. First, use the validate_input_tool to validate the question
2. Then, use the generate_response_tool to get an answer
3. Finally, use the format_answer_tool to format the response nicely

After completing all steps, provide the final formatted answer."""
    
    inputs = {
        "messages": [HumanMessage(content=instructions)]
    }
    
    # Run the agent
    result = app.invoke(inputs)
    
    print("\n=== FINAL RESULT ===")
    print(f"Total messages exchanged: {len(result.get('messages', []))}")
    
    # Extract and display the conversation
    messages = result.get("messages", [])
    for i, msg in enumerate(messages):
        msg_type = type(msg).__name__
        print(f"\n--- Message {i+1} ({msg_type}) ---")
        
        if hasattr(msg, "content") and msg.content:
            print(f"Content: {msg.content[:200]}...")
        
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"Tool Calls: {len(msg.tool_calls)}")
            for tc in msg.tool_calls:
                print(f"  - {tc.get('name', 'unknown')}: {tc.get('args', {})}")
    
    print("\nExecution complete - check Galileo for traces in your project/log stream")

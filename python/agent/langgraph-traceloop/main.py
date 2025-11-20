import os
from typing import TypedDict

# Load environment variables first (contains API keys and project settings)
import dotenv
import openai

# LangGraph imports - this is what we're actually instrumenting
from langgraph.graph import END, StateGraph

# OpenTelemetry imports for custom span attributes
from opentelemetry import trace as trace_api
from traceloop.sdk import Traceloop

dotenv.load_dotenv()

# Configure OpenAI API key
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)
print("✓ OpenAI client configured")

Traceloop.init(
    app_name="LangGraph-Traceloop-Demo",
    disable_batch=False,  # Enable batching for better performance
    resource_attributes={
        "service.version": "1.0.0",
        "deployment.environment": "development",
    },
)

# Get a tracer for creating custom spans
tracer = trace_api.get_tracer(__name__)


class AgentState(TypedDict, total=False):
    user_input: str  # The user's input question
    llm_response: str  # The raw response from the LLM
    parsed_answer: str  # The processed/cleaned answer


# Node 1: Input Validation
# Validates and prepares the user input for processing
def validate_input(state: AgentState):
    user_input = state.get("user_input", "")
    print(f"📥 Validating input: '{user_input}'")

    return {"user_input": user_input}


def generate_response(state: AgentState):
    user_input = state.get("user_input", "")

    try:
        print(f"⚙️ Calling OpenAI with: '{user_input}'")

        # Make the OpenAI API call - Traceloop automatically traces this
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
            max_tokens=300,
            temperature=0.7,
        )

        # Extract the response content
        llm_response = response.choices[0].message.content

        if not llm_response:
            print("❌ No response from OpenAI")
        else:
            print(f"✓ Received response: '{llm_response[:100]}...'")

        return {"llm_response": llm_response}

    except Exception as e:
        print(f"❌ Error calling OpenAI: {e}")
        return {"llm_response": f"Error: {str(e)}"}


def format_answer(state: AgentState):
    llm_response = state.get("llm_response", "")

    # Simple parsing - extract first sentence for a concise answer
    sentences = llm_response.split(". ")
    parsed_answer = sentences[0] if sentences else llm_response

    # Clean up the answer
    parsed_answer = parsed_answer.strip()
    if not parsed_answer.endswith(".") and parsed_answer:
        parsed_answer += "."

    print(f"✨ Parsed answer: '{parsed_answer}'")

    return {"parsed_answer": parsed_answer}


workflow = StateGraph(AgentState)
workflow.add_node("validate_input", validate_input)
workflow.add_node("generate_response", generate_response)
workflow.add_node("format_answer", format_answer)

# Entry point and edges define the control flow of the graph
workflow.set_entry_point("validate_input")
workflow.add_edge("validate_input", "generate_response")
workflow.add_edge("generate_response", "format_answer")
workflow.add_edge("format_answer", END)

# Compile builds the runnable app
app = workflow.compile()

# Run the app and observe traces in both console and Galileo
if __name__ == "__main__":
    # Create a session-level span to group all operations

    inputs = {"user_input": "what moons did galileo discover"}

    result = app.invoke(AgentState(**inputs))

    # Add result attributes with OpenInference-compatible format
    if result.get("llm_response"):
        final_answer = result.get("parsed_answer", result.get("llm_response"))

    print("\n=== FINAL RESULT ===")
    print(f"Question: {result.get('user_input', 'N/A')}")
    print(f"LLM Response: {result.get('llm_response', 'N/A')}")
    print(f"Parsed Answer: {result.get('parsed_answer', 'N/A')}")

    print("✓ Execution complete - check Galileo for traces in your project/log stream")

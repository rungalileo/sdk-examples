import os
from typing import TypedDict

import openai
from langgraph.graph import END, StateGraph

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)
print("✓ OpenAI client configured")


# OpenTelemetry imports for custom span attributes
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


def create_agent():
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

    return app

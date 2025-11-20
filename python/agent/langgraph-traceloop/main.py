import dotenv
from agent import AgentState, create_agent
from traceloop.sdk import Traceloop

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
    inputs = {"user_input": "what moons did galileo discover"}
    app = create_agent()

    result = app.invoke(AgentState(**inputs))

    if result.get("llm_response"):
        final_answer = result.get("parsed_answer", result.get("llm_response"))

    print("\n=== FINAL RESULT ===")
    print(f"Question: {result.get('user_input', 'N/A')}")
    print(f"LLM Response: {result.get('llm_response', 'N/A')}")
    print(f"Parsed Answer: {result.get('parsed_answer', 'N/A')}")

    print("✓ Execution complete - check Galileo for traces in your project/log stream")

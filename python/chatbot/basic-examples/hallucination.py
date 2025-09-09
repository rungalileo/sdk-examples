import os
import json
import time
import openai  # Using the standard OpenAI library
from galileo import GalileoLogger  # Import GalileoLogger for logging
from dotenv import load_dotenv, find_dotenv

# Load environment variables
# 1) load global/shared first
load_dotenv(os.path.expanduser("~/.config/secrets/myapps.env"), override=False)
# 2) then load per-app .env (if present) to override selectively
load_dotenv(find_dotenv(usecwd=True), override=True)

# Initialize the GalileoLogger
logger = GalileoLogger(project="hallucination", log_stream="dev")

# Initialize the standard OpenAI client
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
)

# Questions that might lead to hallucinations
QUESTIONS = [
    "What is inside a black hole?",
    "What will life be like in 100 years?",
    "What was the score of the last Lakers game?",
]

# Different system prompts to test hallucination prevention
SYSTEM_PROMPTS = {"unconstrained": "You are a helpful assistant. Answer the user's questions."}


def generate_response(question: str, system_prompt: str) -> str:
    """Generate a response using the OpenAI API with the given system prompt."""
    # Record the start time for the LLM call
    start_time = time.time_ns()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    # Record the end time for the LLM call
    end_time = time.time_ns()

    response_content = response.choices[0].message.content.strip()

    # Log the LLM call as a span
    logger.add_llm_span(
        input=f"System: {system_prompt}\nUser: {question}",
        output=response_content,
        model="gpt-4o",
        duration_ns=end_time - start_time,
        num_input_tokens=response.usage.prompt_tokens,
        num_output_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens,
    )

    return response_content


def run_hallucination_demo():
    """Run the hallucination demonstration with different prompts and questions."""
    results = []

    for question in QUESTIONS:
        # Start a trace for this question
        trace = logger.start_trace(input=question)

        question_results = {"question": question, "responses": []}

        print(f"\n\n{'='*80}\nQUESTION: {question}\n{'='*80}")

        for prompt_name, system_prompt in SYSTEM_PROMPTS.items():
            # Generate response
            response = generate_response(question, system_prompt)

            # Store results
            question_results["responses"].append({"prompt_type": prompt_name, "response": response})

            # Print results for this question
            print(f"\n--- PROMPT TYPE: {prompt_name} ---")
            print(f"RESPONSE: {response}")

        results.append(question_results)

        # Conclude the trace with a summary of responses
        summary = {
            "question": question,
            "responses": {k: v["response"] for k, v in enumerate(question_results["responses"])},
        }
        logger.conclude(output=json.dumps(summary))

    return results


if __name__ == "__main__":
    print("HALLUCINATION DEMONSTRATION PROGRAM")
    print("This program demonstrates how LLMs can hallucinate and how to prevent it.")
    print("It shows different prompting strategies to reduce hallucinations.")

    # Run the main demonstration
    results = run_hallucination_demo()

    # Flush the traces to Galileo
    logger.flush()

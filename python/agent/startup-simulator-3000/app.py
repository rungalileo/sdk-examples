#!/usr/bin/env python3

import asyncio
import json
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from agent import SimpleAgent
from agent_framework.llm.openai_provider import OpenAIProvider
from agent_framework.llm.models import LLMConfig
from galileo import GalileoLogger

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    """Serve the main page"""
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate_startup():
    """API endpoint to generate startup pitch with individual Galileo trace"""
    try:
        data = request.json
        industry = data.get("industry", "").strip()
        audience = data.get("audience", "").strip()
        random_word = data.get("randomWord", "").strip()
        mode = data.get("mode", "silly").strip()  # Default to silly mode

        # Log API request as JSON
        api_request = {
            "endpoint": "/api/generate",
            "method": "POST",
            "inputs": {
                "industry": industry,
                "audience": audience,
                "random_word": random_word,
                "mode": mode,
            },
        }
        print(f"API Request: {json.dumps(api_request, indent=2)}")

        if not industry or not audience or not random_word:
            return jsonify({"error": "All fields are required"}), 400

        # Initialize Galileo logger for this request
        logger = GalileoLogger(
            project=os.environ.get("GALILEO_PROJECT"),
            log_stream=os.environ.get("GALILEO_LOG_STREAM"),
        )

        # Start individual trace for this request
        trace = logger.start_trace(f"Generate startup pitch - {mode} mode - {industry} targeting {audience}")

        try:
            # Add LLM span for request processing
            logger.add_llm_span(
                input=f"API request received for {mode} mode startup generation",
                output="Request validated and processing started",
                model="flask_api",
                num_input_tokens=len(str(api_request)),
                num_output_tokens=0,
                total_tokens=len(str(api_request)),
                duration_ns=0,
            )

            # Run the agent asynchronously with proper event loop handling
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                agent_result = loop.run_until_complete(run_agent(industry, audience, random_word, mode))
            finally:
                loop.close()

            # Parse the structured JSON result from agent
            try:
                parsed_result = json.loads(agent_result)
                final_output = parsed_result.get("final_output", "No output generated")
            except json.JSONDecodeError:
                # Fallback if result is not JSON
                final_output = str(agent_result)

            # Log API response as JSON
            api_response = {
                "endpoint": "/api/generate",
                "status": "success",
                "result_length": len(final_output),
                "mode": mode,
                "agent_result_preview": (str(agent_result)[:200] + "..." if len(str(agent_result)) > 200 else str(agent_result)),
            }
            print(f"API Response: {json.dumps(api_response, indent=2)}")

            # Add LLM span for successful completion
            logger.add_llm_span(
                input=f"Agent execution completed successfully",
                output=final_output,
                model="flask_api",
                num_input_tokens=len(str(api_request)),
                num_output_tokens=len(final_output),
                total_tokens=len(str(api_request)) + len(final_output),
                duration_ns=0,
            )

            # Conclude the trace successfully
            logger.conclude(output=final_output, duration_ns=0)

            return jsonify({"result": final_output})

        except Exception as e:
            # Add LLM span for error
            logger.add_llm_span(
                input=f"Agent execution failed",
                output=str(e),
                model="flask_api",
                num_input_tokens=len(str(api_request)),
                num_output_tokens=len(str(e)),
                total_tokens=len(str(api_request)) + len(str(e)),
                duration_ns=0,
            )

            # Conclude the trace with error
            logger.conclude(output=str(e), duration_ns=0)

            raise e

    except Exception as e:
        print(f"Error generating startup: {e}")
        return jsonify({"error": str(e)}), 500


async def run_agent(industry: str, audience: str, random_word: str, mode: str = "silly") -> str:
    """Run the agent to generate startup pitch"""
    # Set up LLM provider (this could be updated to use the Galileo-wrapped OpenAI client if desired)
    llm_provider = OpenAIProvider(config=LLMConfig(model="gpt-4", temperature=0.7))

    # Create agent instance with mode
    agent = SimpleAgent(llm_provider=llm_provider, mode=mode)

    # Create different task descriptions based on mode
    if mode == "serious":
        task = (
            f"First, get recent business news context from NewsAPI to understand current market trends, then "
            f"generate a professional startup business plan for a {industry} company targeting {audience} "
            f"that incorporates the concept '{random_word}'. Use the news context to inform market analysis "
            f"and competitive landscape. Make this extremely professional and corporate."
        )
    else:  # silly mode
        task = (
            f"First, get some inspiration from recent HackerNews stories, then "
            f"generate a startup pitch for a {industry} company targeting {audience} "
            f"that includes the word '{random_word}'. Make the pitch creative and "
            f"incorporate relevant trends from the HackerNews stories."
        )

    # Run the agent with individual parameters (Galileo logging handled by individual traces)
    result = await agent.run(task, industry=industry, audience=audience, random_word=random_word)
    return result


if __name__ == "__main__":
    # Verify Galileo configuration
    project_id = os.environ.get("GALILEO_PROJECT")
    log_stream = os.environ.get("GALILEO_LOG_STREAM")
    api_key = os.environ.get("GALILEO_API_KEY")

    print(f"🔍 Galileo Configuration:")
    print(f"   Project: {project_id}")
    print(f"   Log Stream: {log_stream}")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Not Set'}")

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set. Please set this environment variable.")
        exit(1)

    if not api_key:
        print("Warning: GALILEO_API_KEY not set. Galileo logging will be disabled.")

    app.run(debug=True, host="0.0.0.0", port=2021)

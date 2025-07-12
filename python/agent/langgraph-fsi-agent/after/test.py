"""
This file defines a single test that runs the chatbot using the Galileo experiments
framework, with a dataset of questions.

You will need to configure your environment variables to run this test in your .env file.
See the details in the README.md file for how to set up your environment variables.
"""

import json
import os
import time
from typing import Any

from dotenv import load_dotenv

from langchain.schema.runnable.config import RunnableConfig
from langchain_core.callbacks import Callbacks
from langchain_core.messages import HumanMessage

from galileo import GalileoScorers, galileo_context
from galileo.datasets import create_dataset, get_dataset, delete_dataset
from galileo.experiments import get_experiment, run_experiment
from galileo.handlers.langchain import GalileoCallback

from src.galileo_langgraph_fsi_agent.agents.supervisor_agent import (
    create_supervisor_agent,
)

DATASET_NAME = "langgraph-fsi-unit-test-dataset"

def setup_module():
    """
    Setup function that runs once when this test module is executed.

    This will load the environment variables, then ensure we have a valid dataset to run the experiment against.
    """
    print("Setting up test environment...")

    # Load the environment variables from the .env file
    load_dotenv()

    # Verify required environment variables are set
    # You will also need to set up the environment variables for your OpenAI API connection.
    if not os.getenv("GALILEO_PROJECT") or not os.getenv("GALILEO_API_KEY"):
        raise ValueError("GALILEO_PROJECT and GALILEO_API_KEY environment variables are required")

    # Check to see if we already have the dataset, if not we can create it.
    dataset = get_dataset(
        name=DATASET_NAME,
    )

    if dataset is not None:
        delete_dataset(id=dataset.id)
        dataset = None

    # If we don't have the dataset, create it with some canned data. Some of these questions
    # are designed to be factual, while others are designed to be nonsensical or not
    # answerable by the model. This will help us test the correctness and instruction adherence
    # of the model when running the experiment.
    if dataset is None:
        # Load dataset content from JSON file
        with open("./dataset-test.json", "r", encoding="utf-8") as f:
            dataset_content = json.load(f)

        dataset = create_dataset(
            name=DATASET_NAME,
            content=dataset_content,
        )

# Create the supervisor agent
supervisor_agent = create_supervisor_agent()

def send_message_to_supervisor_agent(message: str):
    """
    Send a message to the supervisor agent and return the response.

    This function simulates sending a message to the supervisor agent and getting a response.
    It is used in the test to interact with the chatbot.
    """
    galileo_logger = galileo_context.get_logger_instance()
    callback = GalileoCallback(galileo_logger=galileo_logger, start_new_trace=False, flush_on_chain_end=False)

    messages: dict[str, Any] = {"messages": [HumanMessage(content=message)]}
    callbacks: Callbacks = [callback]
    config: dict[str, Any] = {"configurable": {"thread_id": 42}}

    runnable_config = RunnableConfig(callbacks=callbacks, **config)

    response = supervisor_agent.invoke(input=messages, config=runnable_config)

    return response["messages"][-1].content


def test_run_experiment_with_dataset():
    """
    This test will run the dataset against our chatbot app using the Galileo experiments framework.
    This is designed to show how you can run experiments with a dataset against a real-world application
    to use inside a CI/CD pipeline.

    The default system prompt encourages the assistant to be helpful, but can lead to hallucinations, so
    this test should fail out of the box.

    To make this test pass, you will need to modify the system prompt in the `app.py` file. There is
    a comment in the `app.py` file that shows a better system prompt, which should allow this test to pass.
    """
    # Run the experiment using the canned dataset
    experiment_response = run_experiment(
        # This name is reused, so each experiment run will get a generated name
        # with the run date and time
        experiment_name="langgraph-fsi-experiment",
        dataset_name=DATASET_NAME,
        function=send_message_to_supervisor_agent,
        metrics=[
            GalileoScorers.action_advancement,
            GalileoScorers.action_completion,
            GalileoScorers.tool_error_rate,
            GalileoScorers.tool_selection_quality
        ],
        project=os.getenv("GALILEO_PROJECT"),
    )

    # Poll until we have the results - waiting 5 seconds between polls
    # We need to use the project ID and experiment name from the response as we only have the project name, and the experiment name
    # is generated with a timestamp, so we can't use the name directly.
    experiment = get_experiment(
        project_id=experiment_response["experiment"].project_id,
        experiment_name=experiment_response["experiment"].name,
    )
    while (
        experiment.aggregate_metrics is None # type: ignore
        or "average_agentic_session_success" not in experiment.aggregate_metrics #type: ignore
        or "average_agentic_workflow_success" not in experiment.aggregate_metrics #type: ignore
        or "average_tool_selection_quality" not in experiment.aggregate_metrics #type: ignore
        or "count_tool_error_rate" not in experiment.aggregate_metrics #type: ignore
    ):
        # If we don't have the metrics calculated, Sleep for 5 seconds before polling again
        time.sleep(5)

        # Reload the experiment to see if we have the metrics
        experiment = get_experiment(
            project_id=experiment_response["experiment"].project_id,
            experiment_name=experiment_response["experiment"].name,
        )

    # # Assert the experiment has the expected metric values - each should be 1.0
    # # However, the default system prompt can lead to hallucinations, so this test may fail.
    assert experiment.aggregate_metrics["average_agentic_session_success"] == 1 # type: ignore
    assert experiment.aggregate_metrics["average_agentic_workflow_success"] == 1 # type: ignore
    assert experiment.aggregate_metrics["average_tool_selection_quality"] == 1 # type: ignore
    assert experiment.aggregate_metrics["count_tool_error_rate"] == 0 # type: ignore

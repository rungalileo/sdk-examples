"""
This file defines a single test that runs the chatbot using the Galileo experiments
framework, with a dataset of questions.

You will need to configure your environment variables to run this test in your .env file.
See the details in the README.md file for how to set up your environment variables.
"""

import json
import os
import time

from dotenv import load_dotenv

from galileo import GalileoScorers
from galileo.datasets import create_dataset, get_dataset
from galileo.experiments import get_experiment, run_experiment

from app import chat_with_llm


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
    try:
        dataset = get_dataset(
            name="simple-chatbot-unit-test-dataset",
        )
        print(f"Found existing dataset: {dataset.name if dataset else 'None'}")
    except ValueError:
        # Dataset doesn't exist, so we'll create it
        dataset = None
        print("Dataset not found, will create a new one")

    # If we don't have the dataset, create it with some canned data. Some of these questions
    # are designed to be factual, while others are designed to be nonsensical or not
    # answerable by the model. This will help us test the correctness and instruction adherence
    # of the model when running the experiment.
    if dataset is None:
        try:
            # Load dataset content from JSON file
            print(f"Current working directory: {os.getcwd()}")
            print(f"Checking if ../dataset.json exists: {os.path.exists('../dataset.json')}")
            
            with open("../dataset.json", "r", encoding="utf-8") as f:
                dataset_content = json.load(f)
            
            print(f"Successfully loaded dataset with {len(dataset_content)} items")

            dataset = create_dataset(
                name="simple-chatbot-unit-test-dataset",
                content=dataset_content,
            )
            print(f"Successfully created dataset: {dataset.name if dataset else 'None'}")
        except Exception as e:
            print(f"Failed to create dataset: {e}")
            raise


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
    # Verify the dataset exists before running the experiment
    try:
        dataset = get_dataset(name="simple-chatbot-unit-test-dataset")
        if not dataset:
            raise ValueError("Dataset 'simple-chatbot-unit-test-dataset' not found")
        print(f"Using dataset: {dataset.name}")
    except ValueError as e:
        print(f"Dataset error: {e}")
        # If dataset doesn't exist, create it here as a fallback
        try:
            import json
            with open("../dataset.json", "r", encoding="utf-8") as f:
                dataset_content = json.load(f)
            dataset = create_dataset(
                name="simple-chatbot-unit-test-dataset",
                content=dataset_content,
            )
            print(f"Created fallback dataset: {dataset.name}")
        except Exception as create_error:
            raise ValueError(f"Could not create dataset: {create_error}") from e

    # Run the experiment using the canned dataset
    experiment_response = run_experiment(
        # This name is reused, so each experiment run will get a generated name
        # with the run date and time
        experiment_name="simple-chatbot-experiment",
        dataset=dataset,  # Use the dataset object instead of dataset_name
        function=chat_with_llm,
        metrics=[
            GalileoScorers.correctness,
            GalileoScorers.instruction_adherence,
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
        experiment.aggregate_metrics is None
        or "average_factuality" not in experiment.aggregate_metrics
        or "average_instruction_adherence" not in experiment.aggregate_metrics
    ):
        # If we don't have the metrics calculated, Sleep for 5 seconds before polling again
        time.sleep(5)

        # Reload the experiment to see if we have the metrics
        experiment = get_experiment(
            project_id=experiment_response["experiment"].project_id,
            experiment_name=experiment_response["experiment"].name,
        )

    # Assert the experiment has the expected metric values - each should be 1.0
    # However, the default system prompt can lead to hallucinations, so this test may fail.
    assert experiment.aggregate_metrics["average_instruction_adherence"] == 1
    assert experiment.aggregate_metrics["average_factuality"] == 1

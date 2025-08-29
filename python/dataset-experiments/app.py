"""
Galileo Experiment Runner

This module provides a command-line interface for running Galileo experiments
with custom parameters including project, experiment, dataset, and prompt configurations.
"""

import argparse
import os
from datetime import datetime
from galileo import Message, MessageRole
from galileo.prompts import get_prompt, create_prompt
from galileo.experiments import run_experiment
from galileo.datasets import get_dataset
from dotenv import load_dotenv

load_dotenv()


def main():
    """
    Main function to run Galileo experiments with command-line parameters.

    Parses command-line arguments, creates or retrieves prompt templates,
    fetches datasets, and runs experiments with the specified configuration.
    """
    print("⚠️ Make sure your project & dataset exist.\n")
    parser = argparse.ArgumentParser(
        description="Run a Galileo experiment with custom parameters.",
        epilog='Example: python app.py --project "my-project" \
        --experiment "my-experiment" \
        --dataset "my-dataset" \
        --prompt-template-name "my-prompt" \
        --prompt-content "You are a helpful assistant."',
    )
    parser.add_argument("--project", default="test project", help="Project name")
    parser.add_argument("--experiment", default="test experiment", help="Experiment name")
    parser.add_argument(
        "--prompt-name",
        default="default",
        help='Prompt name (optional, defaults to "default")',
    )
    parser.add_argument("--dataset", default="default", help="Dataset name")
    parser.add_argument(
        "--prompt-content",
        default="You are an assistant. Respond to the user input.",
        help="Prompt content",
    )
    args = parser.parse_args()
    project = args.project
    experiment_name = args.experiment
    prompt_name = args.prompt_name
    dataset_name = args.dataset
    prompt_content = args.prompt_content
    prompt = get_prompt(name=prompt_name)
    if prompt is None:
        try:
            prompt = create_prompt(
                name=prompt_name,
                template=[
                    Message(
                        role=MessageRole.system,
                        content=prompt_content,
                    ),
                    Message(role=MessageRole.user, content="{{input}}"),
                ],
            )
        except Exception as exc:
            # Check if it's an "already exists" error
            if "already exists" in str(exc).lower():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_prompt_name = f"{prompt_name}_{timestamp}"
                print(f"Template '{prompt_name}' already exists. Creating new template: '{new_prompt_name}'")

                prompt = create_prompt(
                    name=new_prompt_name,
                    template=[
                        Message(
                            role=MessageRole.system,
                            content=prompt_content,
                        ),
                        Message(role=MessageRole.user, content="{{input}}"),
                    ],
                )
            else:
                # Re-raise if it's a different error
                raise
    print(f"Fetching dataset with name: {dataset_name}")
    dataset = get_dataset(name=dataset_name)
    run_experiment(
        experiment_name,
        dataset=dataset,
        prompt_template=prompt,
        prompt_settings={
            "max_tokens": 256,
            "model_alias": "GPT-4o",
            "temperature": 0.8,
        },
        metrics=["correctness"],
        project=project,
    )
    print("-" * 60)
    print(f"Experiment '{experiment_name}' completed successfully!")
    print("-" * 60)


if __name__ == "__main__":
    main()

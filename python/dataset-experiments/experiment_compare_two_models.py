"""
This module provides functionality to compare the performance of two LLMs using Galileo experiments.
"""

import os
import json
import sys
import argparse
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
import anthropic
from openai import OpenAI
from galileo import Message, MessageRole
from galileo.prompts import create_prompt, get_prompt_template
from galileo.experiments import run_experiment
from galileo.datasets import create_dataset

load_dotenv()


class ExperimentCompareTwoModels:
    """
    This class is used to create Galileo experiments to compare the performance of two LLMs.
    """

    def __init__(self):
        """
        Initializes the ExperimentCompareTwoModels class with OpenAI and Anthropic clients, and sets up model configurations.
        """
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.galileo_project = os.getenv("GALILEO_PROJECT")

        if not self.galileo_project:
            raise ValueError("GALILEO_PROJECT environment variable is required")

        self.model_configs = {
            "openai": {
                "name": "gpt-4.1-mini",
                "provider": "OpenAI",
                "cost_per_1k_tokens": 0.00015,
                "performance_score": 0.85,
                "context_window": 128000,
                "client": self.openai_client,
            },
            "anthropic": {
                "name": "Claude 3.7 Sonnet",
                "provider": "Anthropic",
                "cost_per_1k_tokens": 0.00015,
                "performance_score": 0.88,
                "context_window": 200000,
                "client": self.anthropic_client,
            },
        }

        # Prompt for simulating an LLM based app - A Data Quality Processor
        self.system_prompt = """You are an expert financial data quality analyst. Your task is to clean and \
        validate financial transaction data.

            Given a financial transaction record, you should:
            1. Identify any data quality issues (missing fields, invalid formats, inconsistencies)
            2. Suggest corrections or flag records that need manual review
            3. Provide confidence scores for your assessments
            4. Estimate the potential financial impact of data quality issues

            Respond with a JSON object containing:
            - "issues_found": List of data quality issues
            - "suggested_corrections": List of suggested fixes
            - "confidence_score": 0-1 score of your assessment confidence
            - "financial_impact": Estimated dollar impact if issues are not fixed
            - "requires_manual_review": Boolean indicating if human review is needed
            - "clean_record": The cleaned transaction record (if possible)

            Focus on accuracy and financial impact assessment.
        """

    def read_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Reads a JSONL file and returns a list of transactions.

        :param file_path: Path to the JSONL file.
        :return: List of transactions.
        """
        transactions = []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if line:
                        try:
                            transaction = json.loads(line)
                            transactions.append(transaction)
                        except json.JSONDecodeError as e:
                            print(f"Warning: Invalid JSON on line {line_num}: {e}")
                            continue

            print(f"Loaded {len(transactions)} transactions from {file_path}")
            return transactions

        except FileNotFoundError as e:
            raise FileNotFoundError(f"JSONL file not found: {file_path}") from e
        except Exception as e:
            raise Exception(f"Error reading JSONL file: {e}") from e

    def create_galileo_dataset(self, transactions: List[Dict[str, Any]], dataset_name: str) -> Any:
        """
        Creates a Galileo dataset from a list of transactions.

        :param transactions: List of transactions.
        :param dataset_name: Name of the dataset.
        :return: Created dataset.
        """
        try:
            dataset_content = []
            for transaction in transactions:
                dataset_content.append({"transaction_data": json.dumps(transaction, ensure_ascii=False)})

            dataset = create_dataset(
                name=dataset_name,
                content=dataset_content,
            )

            print(f"Created Galileo dataset '{dataset_name}' with {len(transactions)} records")
            return dataset

        except Exception as e:
            raise Exception(f"Error creating Galileo dataset: {e}") from e

    def openai_llm_call(self, input_data: str) -> str:
        """
        Calls the OpenAI LLM with the provided input data.

        :param input_data: Input data for the LLM.
        :return: Response from the LLM.
        """
        try:
            response = self.openai_client.responses.create(
                model=self.model_configs["openai"]["name"],
                input=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Process this financial transaction data: {input_data}"},
                ],
                temperature=0.1,
                max_output_tokens=1000,
            )

            text = getattr(response, "output_text", None)
            if text:
                return text

            return str(response)
        except Exception as e:
            return f"Error calling OpenAI API: {e}"

    def anthropic_llm_call(self, input_data: str) -> str:
        """
        Calls the Anthropic LLM with the provided input data.

        :param input_data: Input data for the LLM.
        :return: Response from the LLM.
        """
        try:
            response = self.anthropic_client.messages.create(
                model=self.model_configs["anthropic"]["name"],
                max_tokens=1000,
                temperature=0.8,
                system=self.system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": f"Process this financial transaction data: {input_data}"}],
                    }
                ],
            )
            return response.content[0].text if response.content else ""
        except Exception as e:
            return f"Error calling Anthropic API: {e}"

    def run_model_experiment(self, experiment_name: str, params: Dict[str, Any]) -> None:
        """
        Runs a model experiment using the specified parameters.

        :param experiment_name: Name of the experiment.
        :param params: Dictionary containing dataset, prompt_template, llm_function, and model_config.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            experiment_name = f"{experiment_name}_{timestamp}"
            print(f"Running experiment: {experiment_name}")
            try:

                # 2 types of experiments
                # Runner function experiment: entry point to the app or a function in the codebase.
                # Prompt experiment
                results = run_experiment(
                    experiment_name=experiment_name,
                    dataset=params["dataset"],
                    prompt_template=params["prompt_template"],
                    prompt_settings={"max_tokens": 1000, "model_alias": params["model_config"]["name"], "temperature": 0.8},
                    metrics=["correctness", "structural_correctness_fin_tx"],
                    project=self.galileo_project,
                )

                print(f"Experiment results for {experiment_name}: {results}")

            except Exception as exp_error:
                print(f"Galileo experiment error: {exp_error}")
                print(f"Model used: {params['model_config']['provider']} - {params['model_config']['name']}")

            print(f"Experiment '{experiment_name}' completed successfully!")

        except Exception as e:
            print(f"Error running experiment '{experiment_name}': {e}")
            print(f"Full error details: {type(e).__name__}: {str(e)}")
            print(f"Model config: {params['model_config']}")
            print(f"LLM function: {params['llm_function'].__name__}")

    def run_comparison_experiments(self, jsonl_file_path: str, dataset_name: str = None) -> None:
        """
        Runs comparison experiments using the provided JSONL file and optional dataset name.

        :param jsonl_file_path: Path to the JSONL file.
        :param dataset_name: Optional name for the dataset.
        """
        try:
            transactions = self.read_jsonl_file(jsonl_file_path)

            if not transactions:
                print("No valid transactions found in the JSONL file")
                return

            if not dataset_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dataset_name = f"financial-transactions-{timestamp}"

            dataset = self.create_galileo_dataset(transactions, dataset_name)

            prompt_template = self.get_or_create_prompt_template()

            print("\n" + "=" * 50)
            print("Running OpenAI Experiment")
            print("=" * 50)
            self.run_model_experiment(
                experiment_name="test_openai",
                params={
                    "dataset": dataset,
                    "prompt_template": prompt_template,
                    "llm_function": self.openai_llm_call,
                    "model_config": self.model_configs["openai"],
                },
            )

            print("\n" + "=" * 50)
            print("Running Anthropic Experiment")
            print("=" * 50)
            self.run_model_experiment(
                experiment_name="test_anthropic",
                params={
                    "dataset": dataset,
                    "prompt_template": prompt_template,
                    "llm_function": self.anthropic_llm_call,
                    "model_config": self.model_configs["anthropic"],
                },
            )

            print("\n" + "=" * 50)
            print("All experiments completed.")
            print("=" * 50)

        except Exception as e:
            print(f"Error running comparison experiments: {e}")

    def get_or_create_prompt_template(self) -> Any:
        """
        Retrieves or creates a prompt template for financial data quality.

        :return: Prompt template.
        """
        prompt_name = "finance_data_quality_prompt"

        try:
            prompt_template = get_prompt_template(name=prompt_name)
            print(f"Using existing prompt template: {prompt_name}")
            return prompt_template
        except Exception as e:
            print(f"Creating new prompt template: {prompt_name}")
            prompt_template = create_prompt(
                name=prompt_name,
                template=[
                    Message(role=MessageRole.system, content=self.system_prompt),
                    Message(role=MessageRole.user, content="Process this financial transaction data: {{transaction_data}}"),
                ],
            )
            return prompt_template

    def get_optimal_model(self, context: Dict[str, Any]) -> str:
        """
        Determines the optimal model based on the provided context.

        :param context: Context for model selection.
        :return: Name of the optimal model.
        """
        if context.get("budget_constrained", False):
            return "openai"
        if context.get("high_accuracy_required", False):
            return "anthropic"
        return max(self.model_configs.keys(), key=lambda x: self.model_configs[x]["performance_score"])


def main():
    """
    Main function to execute the intelligent broker system for financial data quality.
    """
    parser = argparse.ArgumentParser(description="Intelligent Broker System for Financial Data Quality")

    parser.add_argument("jsonl_file", help="Path to the JSONL file containing financial transactions")
    parser.add_argument("--dataset-name", help="Optional name for the Galileo dataset")
    parser.add_argument("--project", default=os.getenv("GALILEO_PROJECT"), help="Galileo project name (defaults to GALILEO_PROJECT env var)")

    args = parser.parse_args()

    if not args.project:
        print("Error: Project name must be provided via --project argument or GALILEO_PROJECT environment variable")
        sys.exit(1)

    try:
        broker = ExperimentCompareTwoModels()
        broker.run_comparison_experiments(args.jsonl_file, args.dataset_name)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

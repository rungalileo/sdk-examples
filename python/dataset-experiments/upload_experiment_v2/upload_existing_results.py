"""
Upload Existing Evaluation Results to Galileo

Use this when you've already run evaluations offline and want to upload
the results and traces to Galileo for analysis and visualization.

This is particularly useful when:
- You have historical evaluation data you want to centralize in Galileo
- You ran evaluations with a different tool and want to visualize in Galileo
- You need to replay past evaluations with full tracing for debugging

How it works:
1. Your JSON file contains: question, context (array of chunks), llm_answer, and ground_truth_answer
2. A Galileo dataset is created with just: input (question) and output (ground_truth)
3. During experiment execution, the full data is looked up to create complete traces
4. Galileo metrics are computed and all traces are preserved for analysis with proper chunk attribution

Data Flow:
- Galileo Dataset: Clean inputs for evaluation (question + ground_truth)
- Local JSON: Full execution data for trace reconstruction (with context chunks array)
- Result: Complete evaluation with metrics and detailed traces
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Galileo imports
from galileo.datasets import create_dataset, get_dataset
from galileo.experiments import run_experiment
from galileo.schema.metrics import GalileoScorers
from galileo import galileo_context


def load_evaluation_data(json_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load your existing evaluation results from JSON.

    Creates a lookup dictionary keyed by question for fast access during
    trace reconstruction.

    Expected JSON format:
    [
        {
            "question": "Your question/input",
            "context": ["chunk1", "chunk2", ...] or "single chunk",  # Array of context chunks
            "llm_answer": "The model's response",
            "ground_truth_answer": "Expected correct answer"
        },
        ...
    ]

    Args:
        json_path: Path to JSON file with your evaluation results

    Returns:
        Dict mapping questions to their full evaluation records
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    # Create lookup dict keyed by question
    lookup = {}
    for record in data:
        question = record["question"]
        context = record.get("context", [])

        # Normalize context to always be a list
        if isinstance(context, str):
            context = [context] if context else []
        elif not isinstance(context, list):
            context = [str(context)] if context else []

        lookup[question] = {"context": context, "llm_answer": record.get("llm_answer", ""), "model": record.get("model", "gpt-4o")}  # Allow model override

    return lookup


def create_or_get_dataset(dataset_name: str, evaluation_data: list) -> Any:
    """
    Find existing dataset by name or create a new one.

    This checks if a dataset already exists to avoid duplicates.

    Args:
        dataset_name: Name of the dataset to find or create
        evaluation_data: Data to upload if creating a new dataset

    Returns:
        Dataset object from Galileo
    """
    try:
        dataset = get_dataset(name=dataset_name)
        if dataset is not None:
            print(f"✓ Found existing dataset: '{dataset_name}'")
            return dataset
    except Exception as e:
        # Dataset doesn't exist or error occurred
        if "not found" not in str(e).lower() and "does not exist" not in str(e).lower():
            print(f"Warning: {e}")

    # Create new dataset
    print(f"✓ Creating new dataset: '{dataset_name}'")
    dataset = create_dataset(name=dataset_name, content=evaluation_data)
    print(f"  Uploaded {len(evaluation_data)} rows")
    return dataset


def prepare_dataset_for_galileo(json_path: str, dataset_name: str) -> Any:
    """
    Upload your evaluation data to Galileo as a dataset.

    Only the input (question) and expected output (ground_truth) are uploaded
    to the dataset. The context and llm_answer are preserved locally and will
    be used during trace reconstruction.

    Args:
        json_path: Path to JSON with your evaluation results
        dataset_name: Name for the dataset in Galileo

    Returns:
        Dataset object from Galileo
    """
    # Load your evaluation results
    with open(json_path, "r") as f:
        raw_data = json.load(f)

    # Transform to Galileo dataset format
    # Only include input and expected output for clean evaluation
    galileo_dataset = []
    for row in raw_data:
        galileo_row = {"input": row["question"], "output": row.get("ground_truth_answer", "")}
        galileo_dataset.append(galileo_row)

    return create_or_get_dataset(dataset_name, galileo_dataset)


def create_replay_function(evaluation_lookup: Dict[str, Dict[str, Any]], system_prompt: Optional[str] = None):
    """
    Create a function that replays your evaluation with full tracing.

    This returns a function that Galileo will call for each row in the dataset.
    It reconstructs the full execution trace from your stored results.

    Args:
        evaluation_lookup: Dict mapping questions to their full evaluation data
        system_prompt: Optional system prompt to include in LLM traces

    Returns:
        Function that takes input and returns the LLM answer with full tracing
    """

    # Default system prompt if none provided
    if system_prompt is None:
        system_prompt = "You are a helpful AI assistant. Use the provided context " "to answer the question accurately and concisely."

    def replay_evaluation(input: str, **kwargs) -> str:
        """
        Replay a single evaluation with full trace reconstruction.

        Args:
            input: The question/input from the Galileo dataset

        Returns:
            The LLM answer from your evaluation results
        """
        question = input

        # Look up the full evaluation record
        if question not in evaluation_lookup:
            raise KeyError(f"Question not found in evaluation data: {question[:100]}...")

        eval_record = evaluation_lookup[question]
        context_chunks = eval_record["context"]
        llm_answer = eval_record["llm_answer"]
        model = eval_record.get("model", "gpt-4o")

        # Get Galileo logger for trace reconstruction
        logger = galileo_context.get_logger_instance()

        # Log retriever span if context was used
        if context_chunks:
            logger.add_retriever_span(input=question, output=context_chunks, name="Context Retrieval")

        # Format context chunks for the prompt
        # Join multiple chunks with clear separators
        if context_chunks:
            context_text = "\n\n---\n\n".join([f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(context_chunks)])
        else:
            context_text = ""

        # Log LLM span with full prompt and response
        if context_text:
            full_prompt = f"{system_prompt}\n\nContext:\n{context_text}\n\nQuestion:\n{question}"
        else:
            full_prompt = f"{system_prompt}\n\nQuestion:\n{question}"

        logger.add_llm_span(input=full_prompt, output=llm_answer, model=model, name="Answer Generation")

        # Return the answer for evaluation against ground truth
        return llm_answer

    return replay_evaluation


def upload_experiment(
    dataset: Any, evaluation_data_path: str, project_name: str, run_name: str, system_prompt: Optional[str] = None, metrics: Optional[list] = None
) -> Any:
    """
    Upload your evaluation results as a Galileo experiment.

    This runs an experiment using your existing results, reconstructing
    full traces for visualization and computing Galileo metrics.

    Args:
        dataset: Galileo dataset object
        evaluation_data_path: Path to your JSON file with full evaluation data
        project_name: Galileo project name
        run_name: Name for this experiment run
        system_prompt: Optional system prompt used in your evaluation
        metrics: Optional list of metrics to compute (uses defaults if None)

    Returns:
        Experiment results
    """
    print(f"\nRunning experiment: {run_name}")

    # Load evaluation data for trace reconstruction
    evaluation_lookup = load_evaluation_data(evaluation_data_path)
    print(f"  Loaded {len(evaluation_lookup)} evaluation records")

    # Create replay function with lookup data
    replay_fn = create_replay_function(evaluation_lookup, system_prompt)

    # Use default metrics if none provided
    if metrics is None:
        metrics = [
            GalileoScorers.ground_truth_adherence,
            GalileoScorers.context_adherence,
            GalileoScorers.chunk_attribution_utilization,
            GalileoScorers.completeness,
            GalileoScorers.correctness,
        ]

    # Run experiment with your data
    results = run_experiment(
        run_name,
        project=project_name,
        dataset=dataset,
        function=replay_fn,
        metrics=metrics,
    )

    print(f"✓ Experiment complete!")

    return results


def main():
    """
    Example: Upload existing evaluation results to Galileo

    This script demonstrates how to take evaluation results you already have
    and upload them to Galileo for analysis, visualization, and comparison.

    Steps:
    1. Load your evaluation data from JSON
    2. Create/retrieve a Galileo dataset (input + expected output only)
    3. Run experiment - reconstructs full traces from your stored results
    4. View results in Galileo console with metrics and detailed traces
    """

    # Verify environment configuration
    required_vars = ["GALILEO_API_KEY", "GALILEO_CONSOLE_URL", "GALILEO_PROJECT"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Create a .env file with your Galileo credentials (see .env.example)")
        return

    print("=" * 70)
    print("Upload Existing Evaluation Results to Galileo")
    print("=" * 70)

    # Configuration
    EVALUATION_DATA_PATH = "dataset.json"
    DATASET_NAME = "space-mission-support-qa-2"
    RUN_NAME = "historical-evaluation-upload"
    SYSTEM_PROMPT = (
        "You are a space mission support AI assistant. "
        "Use the provided mission logs and technical context to answer "
        "questions accurately. If the answer is not in the context, "
        "say you don't know rather than speculating."
    )

    # Step 1: Create or retrieve dataset
    print(f"\n📊 Preparing dataset: {DATASET_NAME}")
    dataset = prepare_dataset_for_galileo(EVALUATION_DATA_PATH, DATASET_NAME)

    # Step 2: Upload experiment with full traces
    print(f"\n🚀 Uploading experiment...")
    results = upload_experiment(
        dataset=dataset,
        evaluation_data_path=EVALUATION_DATA_PATH,
        project_name=os.environ.get("GALILEO_PROJECT"),
        run_name=RUN_NAME,
        system_prompt=SYSTEM_PROMPT,
    )

    if results:
        project = os.environ.get("GALILEO_PROJECT")
        console_url = os.environ.get("GALILEO_CONSOLE_URL")
        print(f"\n✅ Success! View your results in Galileo")


if __name__ == "__main__":
    main()

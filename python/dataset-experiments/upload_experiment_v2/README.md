# Upload Existing Evaluation Results to Galileo

This example demonstrates how to upload evaluation results you've already generated to Galileo for analysis, visualization, and comparison.

## Use Case

Sometimes you've already run evaluations—whether with a different tool, offline, or in the past—and you want to centralize and visualize those results in Galileo. This example shows you how to:

- ✅ Upload historical evaluation data to Galileo experiments
- ✅ Reconstruct full execution traces for debugging
- ✅ Compute Galileo metrics on existing results

This is particularly useful when:
- You have legacy evaluation data to migrate to Galileo
- You ran evaluations with custom tooling and want unified visualization
- You need to analyze past model behavior with Galileo's evaluation metrics

## What This Example Does

**The Problem:** Galileo v2 experiments typically run your prompts live, but sometimes you already have the results and just want to upload them.

**The Solution:** This example takes your pre-existing evaluation data (questions, contexts, LLM responses, ground truth) and uploads it to Galileo as a completed experiment with full tracing.

**How it Works:**
1. Your JSON file contains complete evaluation records (question, context chunks array, LLM answer, ground truth)
2. A Galileo dataset is created with inputs and expected outputs
3. An experiment "replays" your results, reconstructing execution traces with proper chunk attribution
4. Galileo computes metrics and provides full visualization

## Data Format

Your evaluation data should be in JSON format with the following structure:

```json
[
  {
    "question": "Your input/question text",
    "context": ["chunk1", "chunk2", "chunk3"],  // Array of context chunks
    "llm_answer": "The response your model generated",
    "ground_truth_answer": "The expected correct answer",
    "model": "gpt-4o"  // Optional: specify the model used
  }
]
```

**Required fields:**
- `question` - The input to your system
- `llm_answer` - The response your system generated
- `ground_truth_answer` - The expected/correct answer

**Optional fields:**
- `context` - Array of retrieved context chunks (for RAG systems).
- `model` - Model identifier (defaults to "gpt-4o" if not specified)

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `env.example` to `.env` and add your Galileo credentials:

```bash
cp env.example .env
```

Edit `.env`:
```
GALILEO_API_KEY=your_api_key_here
GALILEO_CONSOLE_URL=https://app.galileo.ai
GALILEO_PROJECT=your_project_name
```

**Getting your Galileo credentials:**
1. Log in to [Galileo Console](https://app.galileo.ai)
2. Navigate to Settings → API Keys
3. Create a new API key or copy an existing one
4. Create or select a project for your experiments

### 3. Prepare Your Data

Place your evaluation results in `dataset.json` following the format above. See the included example file with space mission support Q&A data.

## Running the Example

```bash
python upload_existing_results.py
```

The script will:
1. ✅ Load your evaluation data from `dataset.json`
2. ✅ Create or retrieve a Galileo dataset
3. ✅ Upload an experiment with full trace reconstruction
4. ✅ Provide a link to view results in the Galileo console

## Customization

### Changing the Dataset

Edit `dataset.json` with your own evaluation data. The example uses space mission support Q&A, but you can use any domain.

### Adjusting Metrics

In `upload_existing_results.py`, modify the `metrics` parameter in `upload_experiment()`:

```python
from galileo.schema.metrics import GalileoScorers

custom_metrics = [
    GalileoScorers.ground_truth_adherence,
    GalileoScorers.context_adherence,
    GalileoScorers.correctness,
    # Add any other Galileo metrics you want
]

upload_experiment(
    dataset=dataset,
    evaluation_data_path="dataset.json",
    project_name=project_name,
    run_name="my-experiment",
    metrics=custom_metrics  # Use your custom metrics
)
```

## What You'll See in Galileo

After running the script, your Galileo project will contain:

- **Dataset**: Your questions and ground truth answers
- **Experiment Run**: Complete execution with:
  - Individual traces for each evaluation
  - Retriever spans
  - LLM spans with prompts and responses
  - Computed metrics (adherence, completeness, correctness, etc.)

## Troubleshooting

### "Missing environment variables"
- Make sure you've created a `.env` file with your Galileo credentials
- Verify all three required variables are set: `GALILEO_API_KEY`, `GALILEO_CONSOLE_URL`, `GALILEO_PROJECT`

### "Question not found in evaluation data"
- Ensure your JSON file has unique questions
- Check that there are no extra whitespace or formatting differences

### Import errors
- Make sure you've activated your virtual environment
- Run `pip install -r requirements.txt` to install all dependencies

### "Dataset already exists"
- The script will automatically use existing datasets with the same name
- To create a fresh dataset, change `DATASET_NAME` in the script

## Learn More

- [Galileo Documentation](https://v2docs.galileo.ai/what-is-galileo)
- [Galileo SDK Reference](https://v2docs.galileo.ai/sdk-api/overview)
- [Creating Custom Metrics](https://v2docs.galileo.ai/concepts/metrics/custom-metrics/custom-metrics-ui-llm)
- [Understanding Experiments](https://v2docs.galileo.ai/sdk-api/experiments/experiments)


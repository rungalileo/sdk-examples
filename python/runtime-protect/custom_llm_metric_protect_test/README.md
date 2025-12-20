# Custom LLM Metric Creation and Runtime Protect Test

This folder contains three scripts that demonstrate how to create, list, test, and delete a custom LLM-based PII-detection metric for Galileo Runtime Protect.

These scripts are intended to show how to register a metric and how Protect stages evaluate inputs using that metric.
They are not a full chatbot or application integration example.

Files:

- `create_pii_metric_sdk.py` — create & register the
`pii_detection` metric via the Galileo Python SDK.

- `test_custom_pii_metric.py` — creates a Protect stage with a ruleset that uses `pii_detection` and tests several inputs.

Util Files:

- `list_metric.py` — helper to check the SDK client for metric-related methods and reminders for manual UI verification.

- `delete_metric.py` — helper to delete the custom LLM metric previously created.  

## Setup

### Step 1: Copy `.env.example` to `.env` and fill in real values

```env
GALILEO_API_KEY="<your-galileo-api-key>"
OPENAI_API_KEY="<your-openai-api-key>"
GALILEO_PROJECT="MyFirstRuntimeProtect"
GALILEO_METRIC="pii_detection"
```

### Step 2: Activate your Python environment and install requirements (if not already installed)

```bash
# from repo root
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Create metric (registers metric in your Galileo org)

```bash
python create_pii_metric_sdk.py
```

### Step 4: Verify metric creation by listing metrics

```bash
python util/list_metrics.py
```

### Step 5: Create stage and run tests against the metric

```bash
python test_custom_pii_metric.py
```

## Notes on UV-style script dependencies (for UI code metrics)

If you plan to create a code-based metric in the Galileo UI (rather than an LLM-based registered metric via the SDK), include a dependency header at the top of your metric file to allow additional packages in the sandbox. Example:

```python
# /// script
# dependencies = [
#   "requests<3",
#   "somepackage==1.2.3",
# ]
# ///
```

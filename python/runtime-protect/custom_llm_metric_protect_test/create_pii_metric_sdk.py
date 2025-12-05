"""
This script creates a custom LLM metric using OpenAI through the SDK instead of the UI.
"""

import os
from dotenv import load_dotenv
from galileo.metrics import create_custom_llm_metric, OutputTypeEnum, StepType

# Load environment variables
load_dotenv()
GALILEO_API_KEY = os.getenv("GALILEO_API_KEY")

# Metric name can be provided via env var GALILEO_METRIC, otherwise use default
METRIC_NAME = os.getenv("GALILEO_METRIC")

if not GALILEO_API_KEY:
    print("❌ GALILEO_API_KEY not set. Please add it to .env")
    exit(1)

print("🚀 Creating custom PII detection metric via SDK...")

try:
    metric_response = create_custom_llm_metric(
        name=METRIC_NAME,
        user_prompt="""
Analyze the following text and detect if it contains Personally Identifiable Information (PII).

PII includes:
- Email addresses (e.g., john@example.com)
- Phone numbers (e.g., 555-123-4567)
- Social Security Numbers (e.g., 123-45-6789)
- Credit card numbers
- Home addresses
- Names with sensitive context

Text to analyze:
{input}

Respond with ONLY "true" if PII is detected, "false" if no PII is detected.
        """,
        node_level=StepType.llm,
        cot_enabled=True,  # Enable chain-of-thought reasoning
        model_name="gpt-4.1-mini",
        num_judges=1,  # Can increase for more robust evaluation
        description="Detects Personally Identifiable Information (PII) in text using LLM evaluation",
        tags=["pii", "security", "protect"],
        output_type=OutputTypeEnum.BOOLEAN
    )
    
    print(f"✅ Metric created successfully!")
    print(f"Metric ID: {metric_response.id if hasattr(metric_response, 'id') else 'N/A'}")
    print(f"Metric Name: {METRIC_NAME}")
    # print(f"Response: {metric_response}")
    
except Exception as e:
    print(f"❌ Error creating metric: {e}")
    exit(1)

print("\n📝 Next steps:")
print("1. Use this metric in your Protect rules:")
print("""
from galileo_core.schemas.protect.rule import Rule, RuleOperator

rule = Rule(
    metric=METRIC_NAME,
    operator=RuleOperator.eq,
    target_value="true"
)
""")

"""
This script creates a stage with the metric registered by create_pii_metric_sdk.py
and tests it with various inputs to verify it works correctly.
"""

from galileo.stages import create_protect_stage, get_protect_stage
from galileo_core.schemas.protect.rule import Rule, RuleOperator
from galileo_core.schemas.protect.ruleset import Ruleset
from galileo_core.schemas.protect.stage import StageType
from galileo_core.schemas.protect.action import OverrideAction
from galileo_core.schemas.protect.payload import Payload
from galileo.protect import invoke_protect

from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Verify environment variables are loaded
print(f"GALILEO_PROJECT: {os.getenv('GALILEO_PROJECT')}")
print(f"GALILEO_API_KEY: {'Set' if os.getenv('GALILEO_API_KEY') else 'Not set'}")

# Create action for when PII is detected
action = OverrideAction(
    choices=[
        "This input contains sensitive information and cannot be processed.",
        "Please remove any personal information before resubmitting.",
        "We cannot process personal information. Please rephrase your request."
    ]
)

# Create rule for PII detection
# Metric name comes from env var GALILEO_METRIC

METRIC_NAME = os.getenv('GALILEO_METRIC')
rule = Rule(
    metric=METRIC_NAME,  # Our custom metric name
    operator=RuleOperator.eq,
    target_value="true"  # Trigger when PII is detected (true)
)

ruleset = Ruleset(rules=[rule])

# Create the stage - explicitly pass project_name if env var not working
project_name = os.getenv('GALILEO_PROJECT') or "MyFirstRuntimeProtect"

# Create the stage with the custom PII detection metric
try:
    stage = create_protect_stage(
        name="PII_Detection_Test_Stage",
        stage_type=StageType.central,
        prioritized_rulesets=[ruleset],
        description="Test the custom PII detection metric"
    )
    print(f"✅ Stage created: {stage}")
except Exception as e:
    print(f"❌ Stage creation error: {e}")
    exit(1)

print("✅ Stage creation completed")

# Wait a moment for the stage to be available
time.sleep(2)

# Verify by retrieving it
try:
    verified_stage = get_protect_stage(
        project_name=project_name,
        stage_name="PII_Detection_Test_Stage"
    )

    if verified_stage:
        print(f"✅ Stage verified: {verified_stage.name}")
        print(f"   Stage ID: {verified_stage.id}")
    else:
        print("❌ Stage not found")
except Exception as e:
    print(f"⚠️  Could not verify stage: {e}")

# Create workflow with Protect
def run_workflow(user_input, description=""):
    # Invoke Protect
    payload = Payload(input=user_input, output="")
    try:
        response = invoke_protect(
            payload=payload,
            project_name=project_name,
            stage_name="PII_Detection_Test_Stage",
            prioritized_rulesets=[ruleset]
        )
        return response
    except Exception as e:
        print(f"   ❌ ERROR invoking protect: {e}")
        return None

# Test cases with and without PII
test_cases = [
    ("Hello, how can I help you today?", "Normal request - no PII"),
    ("My email is john.doe@example.com", "Contains email - HAS PII"),
    ("Call me at 555-123-4567", "Contains phone - HAS PII"),
    ("My SSN is 123-45-6789", "Contains SSN - HAS PII"),
    ("What's the weather like?", "Question - no PII"),
    ("My name is John Doe and I live at 123 Main St", "Contains name and address - HAS PII"),
    ("Can you help me with coding?", "Generic question - no PII"),
    ("Contact: jane.smith@company.com for details", "Contains work email - HAS PII"),
    ("Thanks for your assistance!", "Positive feedback - no PII"),
    ("My credit card is 1234-5678-9012-3456", "Contains card number - HAS PII"),
]

print("\n" + "="*80)
print("🧪 Testing Custom PII Detection Metric")
print("="*80 + "\n")

for i, (test_input, description) in enumerate(test_cases, 1):
    print(f"Test {i}: {description}")
    print(f"   Input: '{test_input}'")
    
    response = run_workflow(test_input, description)
    
    if response:
        print(f"   Status: {response.status}")
        print(f"   Action: {response.action_result.get('type', 'N/A')}")
        
        if response.status.value == 'triggered':
            print(f"   ✅ PII DETECTED - Rule triggered!")
            if response.action_result.get('value'):
                print(f"   Override: {response.action_result['value']}")
        elif response.status.value == 'not_triggered':
            print(f"   ✅ No PII detected - Rule not triggered")
        elif response.status.value == 'skipped':
            print(f"   ⏳ Status: skipped (metric evaluation may be pending)")
        else:
            print(f"   Status: {response.status.value}")
        
        if hasattr(response, 'metric_results') and response.metric_results:
            print(f"   Metric Results: {response.metric_results}")
    
    print()

print("="*80)
print("✅ PII Detection Tests Completed!")
print("="*80)

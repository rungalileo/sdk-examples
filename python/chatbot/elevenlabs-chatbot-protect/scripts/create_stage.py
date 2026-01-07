# Create a Galileo Protect stage for voice guardrails
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory - this sets env vars directly
load_dotenv(Path(__file__).parent.parent / ".env")

# Stage configuration
STAGE_NAME = "voice-guardrails"
STAGE_DESCRIPTION = "Guardrails for voice conversations"

print(f"[CONFIG] GALILEO_CONSOLE_URL: {os.environ.get('GALILEO_CONSOLE_URL', 'not set')}")
print(f"[CONFIG] GALILEO_API_KEY: {os.environ.get('GALILEO_API_KEY', 'not set')[:10]}...")
print(f"[CONFIG] GALILEO_PROJECT_NAME: {os.environ.get('GALILEO_PROJECT_NAME', 'not set')}")

from galileo import (
    GalileoScorers,
    create_protect_stage,
    get_protect_stage,
    Ruleset,
    StageType,
)
from galileo_core.schemas.protect.action import OverrideAction
from galileo_core.schemas.protect.rule import Rule, RuleOperator

# Create a rule: block if input toxicity > 0.2
rule = Rule(metric=GalileoScorers.input_toxicity, operator=RuleOperator.gt, target_value=0.2)

# Override action when triggered
action = OverrideAction(choices=["We're sorry, we can't process your request."])

# Create ruleset with the rule and action
ruleset = Ruleset(rules=[rule], action=action)

# Create the stage
stage = create_protect_stage(
    name=STAGE_NAME,
    stage_type=StageType.central,
    prioritized_rulesets=[ruleset],
    description=STAGE_DESCRIPTION,
)
print(f"\n[SUCCESS] Created stage: {stage}")

# Get the stage ID
stage = get_protect_stage(stage_name=STAGE_NAME)
print(f"\n[INFO] Stage ID: {stage.id}")
print(f"[INFO] Add this to your .env file:")
print(f"GALILEO_PROTECT_STAGE_ID={stage.id}")

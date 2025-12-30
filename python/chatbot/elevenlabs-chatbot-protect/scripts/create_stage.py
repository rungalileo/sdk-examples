# run this to create galileo protect stage
import os
import sys
import logging
from pathlib import Path

# Enable HTTP request logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Show HTTP details
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.DEBUG)

# Add the parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings

# Set Galileo environment variables BEFORE importing galileo
settings = get_settings()
if settings.galileo_console_url:
    os.environ["GALILEO_CONSOLE_URL"] = settings.galileo_console_url
if settings.galileo_api_key:
    os.environ["GALILEO_API_KEY"] = settings.galileo_api_key

# Project name is required - stage will not be created without it
os.environ["GALILEO_PROJECT"] = settings.galileo_project_name


# Stage configuration
STAGE_NAME = "voice-guardrails"
STAGE_DESCRIPTION = "Guardrails for voice conversations"

print(f"[CONFIG] GALILEO_CONSOLE_URL: {os.environ.get('GALILEO_CONSOLE_URL', 'not set')}")
print(f"[CONFIG] GALILEO_API_KEY: {os.environ['GALILEO_API_KEY'][:10]}...")
print(f"[CONFIG] GALILEO_PROJECT: {settings.galileo_project_name}")
# All these are available from the top-level galileo module
from galileo import (
    GalileoScorers,
    create_protect_stage,
    get_protect_stage,
    Ruleset,
    StageType,
)

# These are not re-exported in galileo.__init__, so keep them as-is
from galileo_core.schemas.protect.action import OverrideAction
from galileo_core.schemas.protect.rule import Rule, RuleOperator
#Create a rule
rule = Rule(
    metric=GalileoScorers.input_toxicity,
    operator=RuleOperator.gt,
    target_value=0.2
)

# Create an override action
action = OverrideAction(
    choices=[
        "We're sorry, we can't process your request."
    ]
)

# Add this rule to a ruleset, using the default passthrough action
ruleset = Ruleset(rules=[rule], action=action)

# Create a stage
stage = create_protect_stage(
    name=STAGE_NAME,
    stage_type=StageType.central,
    prioritized_rulesets=[ruleset],
    description=STAGE_DESCRIPTION,
)
print(f"\n[SUCCESS] Created stage: {stage}")

# Verify stage was created
stage = get_protect_stage(stage_name=STAGE_NAME)
print(f"\n[INFO] Stage ID: {stage.id}")
print(f"[INFO] Add this to your .env file:")
print(f"GALILEO_PROTECT_STAGE_ID={stage.id}")
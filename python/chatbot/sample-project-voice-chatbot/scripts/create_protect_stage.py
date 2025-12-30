#!/usr/bin/env python3
"""
=============================================================================
CREATE GALILEO PROTECT STAGE
=============================================================================

This script creates a Galileo Protect guardrail stage for content moderation.

PREREQUISITES:
--------------
1. IMPORTANT!! A Galileo project must already exist in Galileo console.
2. You must have a Galileo API key with access to that project.
3. Set the required environment variables (see below).

REQUIRED ENVIRONMENT VARIABLES:
-------------------------------
  GALILEO_API_KEY       - Your Galileo API key (required)
  GALILEO_CONSOLE_URL   - Galileo console URL (required)
  GALILEO_PROJECT_NAME  - Name of your existing Galileo project (required)

OPTIONAL ENVIRONMENT VARIABLES:
-------------------------------
  GALILEO_PROTECT_STAGE_NAME - Name for the protect stage (default: voice-guardrails)
  TOXICITY_THRESHOLD         - Toxicity score threshold 0.0-1.0 (default: 0.2)

USAGE:
------
  # 1. Ensure ../service/.env has the required variables
  # 2. Run this script:

  python create_protect_stage.py

  # 3. Copy the printed GALILEO_PROTECT_STAGE_ID to ../service/.env

WHAT THIS SCRIPT DOES:
----------------------
1. Connects to your Galileo project
2. Creates a Protect stage with toxicity and PII detection rules
3. If the stage already exists, updates it with the current rulesets (creates new version)
4. When triggered, overrides response with appropriate message
5. Prints the stage ID to add to your environment

=============================================================================
"""

import os
import sys
from pathlib import Path

# Load environment from service/.env (sibling directory)
try:
    from dotenv import load_dotenv
    # Scripts are in scripts/, env is in service/.env
    env_path = Path(__file__).parent.parent / "service" / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[INFO] Loaded environment from {env_path}")
    else:
        print(f"[WARNING] Environment file not found: {env_path}")
        print("         Please create it from service/.env.example")
except ImportError:
    print("[WARNING] python-dotenv not installed. Using system environment variables only.")
    print("         Install with: pip install python-dotenv")

# =============================================================================
# CONFIGURATION (from environment variables)
# =============================================================================

GALILEO_CONSOLE_URL = os.getenv("GALILEO_CONSOLE_URL")
GALILEO_API_KEY = os.getenv("GALILEO_API_KEY")
GALILEO_PROJECT_NAME = os.getenv("GALILEO_PROJECT_NAME")

# Optional configuration with defaults
PROTECT_STAGE_NAME = os.getenv("GALILEO_PROTECT_STAGE_NAME", "voice-guardrails")
TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", "0.2"))

# =============================================================================
# VALIDATION
# =============================================================================

print("=" * 70)
print("CREATE GALILEO PROTECT STAGE")
print("=" * 70)

print(f"\n[CONFIGURATION]")
print(f"  GALILEO_CONSOLE_URL:  {GALILEO_CONSOLE_URL or 'NOT SET'}")
print(f"  GALILEO_API_KEY:      {'***' + GALILEO_API_KEY[-4:] if GALILEO_API_KEY else 'NOT SET'}")
print(f"  GALILEO_PROJECT_NAME: {GALILEO_PROJECT_NAME or 'NOT SET'}")
print(f"  PROTECT_STAGE_NAME:   {PROTECT_STAGE_NAME}")
print(f"  TOXICITY_THRESHOLD:   {TOXICITY_THRESHOLD}")

# Check required variables
missing_vars = []
if not GALILEO_CONSOLE_URL:
    missing_vars.append("GALILEO_CONSOLE_URL")
if not GALILEO_API_KEY:
    missing_vars.append("GALILEO_API_KEY")
if not GALILEO_PROJECT_NAME:
    missing_vars.append("GALILEO_PROJECT_NAME")

if missing_vars:
    print(f"\n[ERROR] Missing required environment variables:")
    for var in missing_vars:
        print(f"  - {var}")
    print("\nPlease set these in ../service/.env file or environment.")
    print("\nExample ../service/.env:")
    print("  GALILEO_CONSOLE_URL=https://your-console.galileo.ai")
    print("  GALILEO_API_KEY=your-api-key-here")
    print("  GALILEO_PROJECT_NAME=your-project-name")
    sys.exit(1)

# =============================================================================
# SET GALILEO ENVIRONMENT (must be done before importing galileo SDK)
# =============================================================================

os.environ["GALILEO_CONSOLE_URL"] = GALILEO_CONSOLE_URL
os.environ["GALILEO_API_KEY"] = GALILEO_API_KEY
os.environ["GALILEO_PROJECT"] = GALILEO_PROJECT_NAME

# =============================================================================
# CREATE PROTECT STAGE
# =============================================================================

print("\n[STEP 1] Importing Galileo SDK...")

try:
    from galileo import (
        GalileoScorers,
        create_protect_stage,
        get_protect_stage,
        update_protect_stage,
        Ruleset,
        StageType,
    )
    from galileo_core.schemas.protect.action import OverrideAction
    from galileo_core.schemas.protect.rule import Rule, RuleOperator
except ImportError as e:
    print(f"\n[ERROR] Failed to import Galileo SDK: {e}")
    print("\nInstall with: pip install galileo")
    sys.exit(1)

print("  Galileo SDK imported successfully.")

print("\n[STEP 2] Creating guardrail rules...")

# RULESET 1: Toxicity Detection
toxicity_rule = Rule(
    metric=GalileoScorers.input_toxicity,
    operator=RuleOperator.gt,
    target_value=TOXICITY_THRESHOLD
)
print(f"  Ruleset 1 - Toxicity: {GalileoScorers.input_toxicity} > {TOXICITY_THRESHOLD}")

toxicity_action = OverrideAction(
    choices=[
        "I'm sorry, but I can't respond to that kind of language. Let's keep our conversation respectful.",
        "That's not appropriate. I'm here to help, but I need you to communicate respectfully.",
        "I don't respond to toxic language. Please rephrase your question politely."
    ]
)

toxicity_ruleset = Ruleset(rules=[toxicity_rule], action=toxicity_action)

# RULESET 2: PII Detection
pii_rule = Rule(
    metric=GalileoScorers.input_pii,
    operator=RuleOperator.any,
    target_value=["ssn", "address", "credit_card", "phone_number"]
)
print(f"  Ruleset 2 - PII: {GalileoScorers.input_pii} contains sensitive data")

pii_action = OverrideAction(
    choices=[
        "I've detected personally identifiable information in your message. For your privacy and security, I cannot process this request. Please remove any sensitive information and try again."
    ]
)

pii_ruleset = Ruleset(rules=[pii_rule], action=pii_action)

print("  Created 2 separate rulesets (each can trigger independently)")

print(f"\n[STEP 3] Creating Protect stage '{PROTECT_STAGE_NAME}'...")

try:
    # Create the Protect stage with BOTH rulesets
    # Each ruleset can trigger independently (OR logic)
    stage = create_protect_stage(
        name=PROTECT_STAGE_NAME,
        stage_type=StageType.central,
        prioritized_rulesets=[toxicity_ruleset, pii_ruleset],
        description=f"Guardrails for {GALILEO_PROJECT_NAME} - blocks toxic input and PII."
    )

    # Handle case where create_protect_stage returns None (stage may already exist)
    if stage is None:
        raise Exception("Stage may already exist (create returned None)")

    print(f"\n" + "=" * 70)
    print("SUCCESS! Protect stage created.")
    print("=" * 70)
    print(f"\n  Stage Name: {stage.name}")
    print(f"  Stage ID:   {stage.id}")
    print(f"  Stage Type: {stage.type}")

    print(f"\n" + "-" * 70)
    print("NEXT STEP: Add this to ../service/.env file:")
    print("-" * 70)
    print(f"\nGALILEO_PROTECT_STAGE_ID={stage.id}")
    print()

except Exception as e:
    print(f"\n[INFO] Could not create new stage: {e}")

    # Check if stage already exists and update it
    print(f"\n[STEP 4] Checking if stage '{PROTECT_STAGE_NAME}' already exists...")
    try:
        existing_stage = get_protect_stage(stage_name=PROTECT_STAGE_NAME)
        if existing_stage:
            print(f"  Found existing stage: {existing_stage.name} (ID: {existing_stage.id})")

            # Show key stage properties
            print(f"\n  [DEBUG] Stage properties:")
            for attr in ['id', 'name', 'type', 'version', 'description', 'paused', 'project_id', 'created_by']:
                if hasattr(existing_stage, attr):
                    print(f"    {attr}: {getattr(existing_stage, attr)}")

            # Show existing rulesets info
            if hasattr(existing_stage, 'prioritized_rulesets') and existing_stage.prioritized_rulesets:
                print(f"  Current rulesets: {len(existing_stage.prioritized_rulesets)}")
                for i, rs in enumerate(existing_stage.prioritized_rulesets, 1):
                    if hasattr(rs, 'rules') and rs.rules:
                        rule_metrics = [r.metric if hasattr(r, 'metric') else 'unknown' for r in rs.rules]
                        print(f"    - Ruleset {i}: {rule_metrics}")
            else:
                print(f"  Current rulesets: None or not accessible")

            print(f"\n[STEP 5] Updating existing stage with current rulesets...")
            print(f"  New rulesets:")
            print(f"    - Ruleset 1: {GalileoScorers.input_toxicity} > {TOXICITY_THRESHOLD}")
            print(f"    - Ruleset 2: {GalileoScorers.input_pii} (ssn, address, credit_card, phone_number)")

            # Update the existing stage with the new rulesets
            # Note: update_protect_stage doesn't accept description parameter
            updated_stage = update_protect_stage(
                stage_name=PROTECT_STAGE_NAME,
                prioritized_rulesets=[toxicity_ruleset, pii_ruleset],
            )

            print(f"\n" + "=" * 70)
            print("SUCCESS! Protect stage updated with new rulesets.")
            print("=" * 70)

            # Handle case where update returns None but succeeded
            if updated_stage:
                print(f"\n  Stage Name: {updated_stage.name}")
                print(f"  Stage ID:   {updated_stage.id}")
                print(f"  Version:    {updated_stage.version}")
            else:
                print(f"\n  Stage Name: {existing_stage.name}")
                print(f"  Stage ID:   {existing_stage.id}")
                print(f"  (Update returned None but likely succeeded)")

            stage_id = updated_stage.id if updated_stage else existing_stage.id
            print(f"\n" + "-" * 70)
            print("Your ../service/.env should have:")
            print("-" * 70)
            print(f"\nGALILEO_PROTECT_STAGE_ID={stage_id}")
            print()
            sys.exit(0)
        else:
            print("  Stage not found.")
    except Exception as e2:
        print(f"  Could not update existing stage: {e2}")

    sys.exit(1)

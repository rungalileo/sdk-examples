#!/usr/bin/env python3
"""
Galileo Data Redaction Demo
===========================

A self-contained, runnable demonstration of how client-side data redaction
works with Galileo. Safe to run in a customer environment.

WHAT THIS SHOWS
---------------
1. You scrub sensitive data (PII/NPI) on YOUR side, before it ever leaves
   your network, using your own patterns (regex shown here; swap in Presidio,
   Private AI, etc. if you prefer).
2. You send BOTH the raw value (`input`/`output`) and the scrubbed value
   (`redacted_input`/`redacted_output`) to Galileo.
3. Galileo stores both. Privileged users see the raw value in the UI;
   users who shouldn't see sensitive data are shown the redacted value.
   (This UI swap is governed by org-level RBAC redaction rules, configured
   separately by an admin / forward-deployed engineer.)
4. The evaluation engine reads the raw value, so metric quality is unaffected.

KEY POINTS FOR A SECURITY REVIEW
--------------------------------
- Galileo does NOT auto-detect or auto-mask PII. The masking logic is YOURS.
- Redaction is an ACCESS-CONTROL feature (who can VIEW raw), not data removal.
  If raw data must never reach Galileo at all, do NOT send it as `input` --
  send only the scrubbed value (see the OPTIONAL section at the bottom).
- Encryption at rest is a separate, storage-layer control and is configured
  per-deployment; it does not affect this flow.

PREREQUISITES
-------------
    pip install galileo python-dotenv

ENVIRONMENT VARIABLES (set these, or put them in a .env file)
-------------------------------------------------------------
    GALILEO_API_KEY      Your Galileo API key
    GALILEO_PROJECT      Target project name
    GALILEO_LOG_STREAM   Target log stream name
    GALILEO_CONSOLE_URL  (self-hosted only) e.g. https://console.galileo.yourbank.com

RUN
---
    python redaction-demo.py
"""

import os
import re
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()  # optional: load config from a local .env file
except ImportError:
    pass  # python-dotenv is optional; env vars can be set directly

from galileo import GalileoLogger


# ---------------------------------------------------------------------------
# 1) YOUR redaction logic.
#
#    This is the part the CUSTOMER owns. Replace / extend these patterns with
#    the regex list your security team provides. Each entry maps a label to a
#    pattern; matches are replaced with a clearly-marked placeholder so the
#    redacted text stays human-readable (and non-empty -- Galileo ignores an
#    empty redacted value and would fall back to showing the raw value).
# ---------------------------------------------------------------------------
PII_PATTERNS: dict[str, re.Pattern] = {
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "PHONE": re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),
    "ACCOUNT": re.compile(r"\b\d{10,16}\b"),  # e.g. card / account numbers
}


def redact(text: str) -> str:
    """Return a copy of `text` with all known sensitive patterns replaced.

    Replaces each match with a labelled placeholder, e.g. "[SSN]", so it is
    obvious in the UI what was removed and the eval/display still has context.
    """
    if not text:
        return text
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label}]", text)
    return text


# ---------------------------------------------------------------------------
# 2) A pretend application turn containing sensitive data.
# ---------------------------------------------------------------------------
RAW_INPUT = (
    "Hi, my name is Jane Doe. My SSN is 123-45-6789, my email is "
    "jane.doe@example.com, and my account number is 4111111111111111. "
    "Can you confirm my balance?"
)
RAW_OUTPUT = (
    "Thanks Jane. I've confirmed the account ending 1111 tied to "
    "jane.doe@example.com. Your balance is $4,210.55."
)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        sys.exit(f"ERROR: required environment variable {name} is not set.")
    return value


def main() -> None:
    project = require_env("GALILEO_PROJECT")
    log_stream = require_env("GALILEO_LOG_STREAM")

    # Build the redacted versions on the client side.
    redacted_input = redact(RAW_INPUT)
    redacted_output = redact(RAW_OUTPUT)

    # Show the customer exactly what gets scrubbed, before anything is sent.
    print("=" * 72)
    print("CLIENT-SIDE REDACTION (happens in YOUR environment, before send)")
    print("=" * 72)
    print("\n-- RAW INPUT (what your app saw) --")
    print(RAW_INPUT)
    print("\n-- REDACTED INPUT (what unprivileged UI users will see) --")
    print(redacted_input)
    print("\n-- RAW OUTPUT --")
    print(RAW_OUTPUT)
    print("\n-- REDACTED OUTPUT --")
    print(redacted_output)
    print()

    # -----------------------------------------------------------------------
    # 3) Log the trace, sending BOTH raw and redacted values.
    #    Galileo stores both; RBAC rules decide which one each viewer sees.
    # -----------------------------------------------------------------------
    logger = GalileoLogger(project=project, log_stream=log_stream)

    logger.start_trace(
        input=RAW_INPUT,
        redacted_input=redacted_input,
        name="redaction_demo_trace",
    )

    logger.add_llm_span(
        input=RAW_INPUT,
        output=RAW_OUTPUT,
        redacted_input=redacted_input,
        redacted_output=redacted_output,
        model="gpt-4o",
        name="assistant_response",
    )

    logger.conclude(
        output=RAW_OUTPUT,
        redacted_output=redacted_output,
    )

    logger.flush()  # send the trace to Galileo

    print("=" * 72)
    print("SENT TO GALILEO")
    print("=" * 72)
    print(f"Project    : {project}")
    print(f"Log stream : {log_stream}")
    print(
        "\nIn the Galileo UI:\n"
        "  - A privileged user sees the RAW input/output.\n"
        "  - A user covered by a redaction rule sees the REDACTED version.\n"
        "  - Evaluators score the RAW values, so metric quality is unaffected.\n"
    )

    # -----------------------------------------------------------------------
    # OPTIONAL -- strict data-minimization variant.
    #
    # If your requirement is that RAW sensitive data must NEVER reach Galileo
    # (not just hidden in the UI), do NOT send it at all -- put the scrubbed
    # value directly in `input`/`output` and omit the redacted_* fields:
    #
    #     logger.add_llm_span(
    #         input=redacted_input,     # only the scrubbed value is sent
    #         output=redacted_output,
    #         model="gpt-4o",
    #     )
    #
    # Trade-off: evaluators then score the redacted text, which can reduce
    # eval accuracy for prompts where the removed value matters.
    # -----------------------------------------------------------------------


if __name__ == "__main__":
    main()

"""
Verify that a custom metric was created successfully

This helper probes the installed `galileo` package for scorer/metric listing
APIs and prints manual verification steps if programmatic listing isn't available.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GALILEO_API_KEY = os.getenv("GALILEO_API_KEY")

if not GALILEO_API_KEY:
    print("❌ GALILEO_API_KEY not set. Please add it to .env")
    exit(1)

try:
    import galileo
except Exception as e:
    print(f"⚠️  Could not import 'galileo' package: {e}")
    print("Please install the package in the active venv: python -m pip install galileo galileo-core")
    print("You can still verify the metric manually at https://app.galileo.ai")
    exit(1)

try:
    # Try galileo.scorers.Scorers().list()
    if hasattr(galileo, "scorers"):
        try:
            sc_client = galileo.scorers.Scorers()
            resp = sc_client.list()
            if hasattr(resp, "scorers"):
                items = resp.scorers
            elif hasattr(resp, "items"):
                items = resp.items
            elif isinstance(resp, list):
                items = resp
            else:
                try:
                    items = list(resp)
                except Exception:
                    items = []

            print(f"✅ Found {len(items)} registered scorers (showing names where available):")
            for it in items[:50]:
                name = getattr(it, "name", None) or getattr(it, "scorer_name", None) or getattr(it, "title", None)
                sid = getattr(it, "id", None) or getattr(it, "scorer_id", None)
                print(f" - {name} (id={sid})")

            print("\nIf you see 'pii_detection' in the list above, the metric is registered.")
            exit(0)
        except Exception as e:
            print(f"⚠️  scorers.Scorers().list() failed: {e}")

    # Try galileo.metrics.list_scorers()
    if hasattr(galileo, "metrics"):
        try:
            metrics_mod = galileo.metrics
            print("ℹ️  Using galileo.metrics to list registered scorers (if supported)...")
            if hasattr(metrics_mod, "list_scorers"):
                try:
                    resp = metrics_mod.list_scorers()
                    items = getattr(resp, "scorers", None) or getattr(resp, "items", None) or resp
                    print(f"✅ metrics.list_scorers() returned {len(items) if items else 0} items (showing up to 50):")
                    for it in (items or [])[:50]:
                        name = getattr(it, "name", None)
                        sid = getattr(it, "id", None)
                        print(f" - {name} (id={sid})")
                    print("\nIf you see 'pii_detection' in the list above, the metric is registered.")
                    exit(0)
                except Exception as e:
                    print(f"⚠️  metrics.list_scorers() failed: {e}")
        except Exception as e:
            print(f"⚠️  Could not inspect galileo.metrics: {e}")

    # Fallback: print likely-relevant attributes on the galileo package
    print("\n⚠️  Could not enumerate scorers programmatically with this SDK version.")
    print("Available top-level attributes on the 'galileo' package that may be useful:")
    for a in sorted([m for m in dir(galileo) if not m.startswith("_")]):
        if "scor" in a.lower() or "metric" in a.lower() or "metrics" in a.lower():
            print(f" - {a}")

    print("\nManual verification steps:")
    print("1. Go to https://app.galileo.ai and sign in to your org.")
    print("2. Navigate to the 'Metrics' or 'Scorers' section.")
    print("3. Search for the metric named: 'pii_detection' and verify status and settings.")

except Exception as e:
    print(f"Unexpected error while probing galileo package: {e}")
    print("You can still verify the metric in the Galileo UI: https://app.galileo.ai")

import os
import sys
from galileo.metrics import delete_metric
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get metric name from environment variable
metric_name = os.getenv("GALILEO_METRIC")
if not metric_name:
    print("❌ GALILEO_METRIC not set in .env")
    sys.exit(1)

# Delete the metric with simple try/except and user-visible result
try:
    delete_metric(name=metric_name)
    print(f"✅ Deleted metric: {metric_name}")
except Exception as e:
    print(f"❌ Failed to delete metric '{metric_name}': {e}")

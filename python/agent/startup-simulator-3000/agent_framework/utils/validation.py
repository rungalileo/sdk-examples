from typing import Any
import json
from agent_framework.llm.models import LLMMessage
from datetime import datetime

def ensure_valid_io(data: Any) -> str:
    """Ensure data is in a valid format for Galileo Step IO"""
    if data is None:
        return "{}"
    if isinstance(data, str):
        return data
    if isinstance(data, datetime):
        return json.dumps(data.isoformat())
    if isinstance(data, (dict, list)):
        # Handle nested structures that might contain datetime objects
        def format_value(v: Any) -> Any:
            if isinstance(v, datetime):
                return v.isoformat()
            if isinstance(v, dict):
                return {k: format_value(v) for k, v in v.items()}
            if isinstance(v, list):
                return [format_value(x) for x in v]
            return v
        return json.dumps(format_value(data))
    if isinstance(data, LLMMessage):
        return json.dumps({"role": data.role, "content": data.content})
    return json.dumps({"content": str(data)})
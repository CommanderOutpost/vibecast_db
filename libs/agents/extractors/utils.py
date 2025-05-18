# libs/agents/extractors/utils.py
import json
import re


def sanitize_json_output(raw: str):
    """
    Return the first JSON object or array found in `raw` model output.
    Raises ValueError if no JSON is found or if parsing fails.
    """
    match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in model output")
    blob = match.group(1)
    try:
        return json.loads(blob)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")

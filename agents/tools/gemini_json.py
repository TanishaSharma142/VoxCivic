import json
from typing import Any


def parse_gemini_json(response_text: str) -> Any:
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to recover by extracting first JSON-looking substring
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end != -1 and start < end:
            try:
                return json.loads(response_text[start:end + 1])
            except json.JSONDecodeError:
                return None
    return None


def validate_schema(parsed: Any, required_keys: list[str]) -> bool:
    if not isinstance(parsed, dict):
        return False
    return all(key in parsed for key in required_keys)

"""
Robust JSON parsing, fence stripping, and repair helpers for LLM responses.
"""

import json
import re
from typing import Any, Dict, Optional


def extract_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to parse JSON from an LLM response string.
    Handles markdown fences (```json ... ```), leading/trailing whitespace,
    and embedded JSON objects.
    """
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # Strip markdown code blocks
    fence_pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.search(fence_pattern, cleaned, re.MULTILINE)
    if match:
        cleaned = match.group(1).strip()

    # Try direct parse
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Find the outermost balanced curly braces
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = cleaned[start : end + 1]
        try:
            data = json.loads(snippet)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        # Attempt basic repair: remove trailing commas before closing braces/brackets
        repaired = re.sub(r",\s*([}\]])", r"\1", snippet)
        try:
            data = json.loads(repaired)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    return None


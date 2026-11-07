"""
Safety, redacting, and verification filters for AI inputs and outputs.
Enforces that no sensitive credentials leak, human help remains permission-based,
and citations match verified context.
"""

from typing import Any, Dict, List, Set
from .privacy import mask_pii_for_cloud
from .schemas import AssistanceResponse


def filter_source_refs(model_refs: List[str], valid_ids: Set[str]) -> List[str]:
    """Ensures source_refs only contains IDs that were provided in verified_context."""
    if not valid_ids or not model_refs:
        return []
    seen = set()
    filtered = []
    for ref in model_refs:
        ref_clean = str(ref).strip()
        if ref_clean in valid_ids and ref_clean not in seen:
            seen.add(ref_clean)
            filtered.append(ref_clean)
    return filtered


def scrub_credentials(text: str) -> str:
    """Scrubs any accidental echo of credentials or sensitive PII from assistant text."""
    if not text:
        return ""
    masked, _ = mask_pii_for_cloud(text)
    return masked


def sanitize_response(
    data: Dict[str, Any],
    valid_source_ids: Set[str],
    expected_language: str,
    expected_module: str,
    privacy_notices: List[str] = None,
) -> AssistanceResponse:
    """
    Validates and cleans the dictionary against response contract rules:
    - Enforces language & module match
    - Filters source_refs strictly to provided verified_context IDs
    - Scrubs any sensitive credentials from user-facing text
    - Appends any local privacy notices to warnings
    - Ensures human assistance is permission-based and optional
    """
    data["language"] = expected_language
    data["module"] = expected_module

    # Clean text fields
    data["reply"] = scrub_credentials(str(data.get("reply", "")).strip())

    raw_steps = data.get("steps") or []
    data["steps"] = [
        scrub_credentials(str(step).strip())
        for step in raw_steps
        if str(step).strip()
    ]

    raw_warnings = data.get("warnings") or []
    cleaned_warnings = [
        scrub_credentials(str(w).strip())
        for w in raw_warnings
        if str(w).strip()
    ]

    # Add local privacy notices if present
    if privacy_notices:
        for notice in privacy_notices:
            if notice not in cleaned_warnings:
                cleaned_warnings.append(notice)
    data["warnings"] = cleaned_warnings

    # Filter source refs against verified context
    raw_refs = data.get("source_refs") or []
    data["source_refs"] = filter_source_refs(raw_refs, valid_source_ids)

    # Boolean flag
    data["needs_human_help"] = bool(data.get("needs_human_help", False))

    # Follow up question
    raw_fu = data.get("follow_up_question")
    if raw_fu and str(raw_fu).strip() and str(raw_fu).strip().lower() not in ("none", "null"):
        data["follow_up_question"] = scrub_credentials(str(raw_fu).strip())
    else:
        data["follow_up_question"] = None

    return AssistanceResponse(**data)


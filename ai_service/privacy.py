"""
Privacy and PII preprocessing layer for Kerala Accessibility Assistant.
Enforces local/on-device privacy boundaries before any cloud AI API call.
"""

import re
from typing import List, Tuple

# Aadhaar: 12 digits, often formatted as 4-4-4
AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[\s\-]?\d{4}[\s\-]?\d{4}\b")

# Indian mobile phone numbers: optional +91, starts with 6, 7, 8, or 9, followed by 9 digits
PHONE_PATTERN = re.compile(r"(?:\+91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b")

# Credit/Debit cards
CARD_PATTERN = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")

# OTP, PIN, CVV, passwords
CREDENTIAL_PATTERN = re.compile(
    r"\b(?:otp|one-time password|pin|cvv|password|passwd)[\s:=#\-]*([A-Za-z0-9@#$]{3,8})\b",
    re.IGNORECASE,
)

# Email addresses
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")


def mask_pii_for_cloud(text: str) -> Tuple[str, List[str]]:
    """
    Masks personally identifiable information (PII) before any cloud AI API call.
    Returns:
        (masked_text, detected_privacy_notices)

    Safety Note: Pattern matching alone cannot reliably detect every proper name or address.
    This local masking acts as a defense-in-depth barrier.
    """
    if not text:
        return "", []

    notices: List[str] = []
    masked = text

    if AADHAAR_PATTERN.search(masked):
        masked = AADHAAR_PATTERN.sub("[AADHAAR_MASKED]", masked)
        notices.append("Aadhaar number detected and masked for privacy.")

    if PHONE_PATTERN.search(masked):
        masked = PHONE_PATTERN.sub("[PHONE_MASKED]", masked)
        notices.append("Phone number detected and masked for privacy.")

    if CARD_PATTERN.search(masked):
        masked = CARD_PATTERN.sub("[CARD_MASKED]", masked)
        notices.append("Financial card details detected and masked for privacy.")

    if CREDENTIAL_PATTERN.search(masked):
        masked = CREDENTIAL_PATTERN.sub("[SECURITY_CODE_MASKED]", masked)
        notices.append("Security credential / OTP detected and masked for privacy.")

    if EMAIL_PATTERN.search(masked):
        masked = EMAIL_PATTERN.sub("[EMAIL_MASKED]", masked)
        notices.append("Email address detected and masked for privacy.")

    return masked, notices


def validate_privacy_compliance(text: str) -> Tuple[bool, List[str]]:
    """
    Backend validation to ensure no raw unmasked credentials or Aadhaar numbers
    are passed to cloud models.
    """
    violations = []
    if AADHAAR_PATTERN.search(text):
        violations.append("Raw Aadhaar number present.")
    if CARD_PATTERN.search(text):
        violations.append("Raw card number present.")
    if CREDENTIAL_PATTERN.search(text):
        violations.append("Raw security credential / OTP present.")

    is_compliant = len(violations) == 0
    return is_compliant, violations


def safe_summary_for_logs(text: str, max_chars: int = 40) -> str:
    """
    Returns an anonymized, truncated snippet suitable for operational logging.
    Never logs full user input, credentials, or personal records.
    """
    if not text:
        return "<empty>"
    masked, _ = mask_pii_for_cloud(text)
    snippet = masked[:max_chars].replace("\n", " ").strip()
    return f"'{snippet}...' (length={len(text)})"


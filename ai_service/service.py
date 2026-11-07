"""
Core service implementation of generate_assistance for Member 3.
Complies strictly with the service contract, Kerala accessibility guidelines,
language constraints, on-device privacy masking, and safety requirements.
"""

import concurrent.futures
import logging
from typing import Any, Dict, List, Optional, Set, Union

from .config import AIServiceConfig
from .privacy import (
    mask_pii_for_cloud,
    safe_summary_for_logs,
    validate_privacy_compliance,
)
from .providers.gemini_provider import GeminiProvider
from .providers.mock_provider import MockProvider
from .providers.openai_provider import OpenAIProvider
from .sanitizer import sanitize_response
from .schemas import (
    ALLOWED_LANGUAGES,
    ALLOWED_MODULES,
    AssistanceModule,
    AssistanceResponse,
    SupportedLanguage,
    VerifiedExcerpt,
)

logger = logging.getLogger("ai_service")


def _normalize_language(lang: Optional[str]) -> str:
    """Normalizes input language to 'ml' or 'en'."""
    if not lang:
        return "en"
    cleaned = str(lang).strip().lower()
    if cleaned in ("ml", "malayalam", "mal"):
        return "ml"
    if cleaned in ("en", "english"):
        return "en"
    return "en"


def _normalize_module(mod: Optional[str]) -> str:
    """Normalizes input module to one of the 5 allowed modules."""
    if not mod:
        return "human_help"
    cleaned = str(mod).strip().lower().replace("-", "_").replace(" ", "_")
    if cleaned in ALLOWED_MODULES:
        return cleaned
    return "human_help"


def _normalize_verified_context(
    raw_context: Optional[List[Union[Dict[str, Any], VerifiedExcerpt, Any]]]
) -> List[VerifiedExcerpt]:
    """Converts diverse context representations into a list of VerifiedExcerpt."""
    if not raw_context:
        return []

    results: List[VerifiedExcerpt] = []
    for idx, item in enumerate(raw_context):
        if isinstance(item, VerifiedExcerpt):
            results.append(item)
        elif isinstance(item, dict):
            item_id = str(item.get("id") or item.get("source_id") or item.get("source") or f"src_{idx + 1}").strip()
            text = str(item.get("text") or item.get("content") or item.get("snippet") or "").strip()
            title = item.get("title")
            if text:
                results.append(VerifiedExcerpt(id=item_id, text=text, title=title))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            results.append(VerifiedExcerpt(id=str(item[0]).strip(), text=str(item[1]).strip()))
        elif isinstance(item, str) and item.strip():
            results.append(VerifiedExcerpt(id=f"src_{idx + 1}", text=item.strip()))

    return results


def _build_empty_input_fallback(module: str, language: str) -> Dict[str, Any]:
    """Fallback response when the user provides empty or whitespace-only input."""
    if language == "ml":
        return {
            "language": "ml",
            "module": module,
            "reply": "നിങ്ങൾക്ക് എന്താണ് സഹായം വേണ്ടതെന്ന് ദയവായി വ്യക്തമാക്കുക. സഹായിക്കാൻ ഞാൻ തയ്യാറാണ്.",
            "steps": [],
            "warnings": ["ചോദ്യങ്ങളോ വിവരങ്ങളോ നൽകിയിട്ടില്ല."],
            "source_refs": [],
            "needs_human_help": False,
            "follow_up_question": "ഇന്ന് എന്ത് കാര്യത്തിലാണ് നിങ്ങൾക്ക് സഹായം വേണ്ടത്?",
        }
    return {
        "language": "en",
        "module": module,
        "reply": "Please share what you need help with. I am here to assist you.",
        "steps": [],
        "warnings": ["No input text was provided."],
        "source_refs": [],
        "needs_human_help": False,
        "follow_up_question": "What would you like assistance with today?",
    }


def _build_privacy_rejected_fallback(module: str, language: str, reason: str) -> Dict[str, Any]:
    """Fallback response when unmasked sensitive credentials or PII cannot be safely forwarded."""
    if language == "ml":
        return {
            "language": "ml",
            "module": module,
            "reply": "നിങ്ങളുടെ സ്വകാര്യത സംരക്ഷിക്കുന്നതിനായി, ആധാർ നമ്പർ, ഒടിപി, അല്ലെങ്കിൽ പാസ്‌വേഡ് തുടങ്ങിയ വിവരങ്ങൾ ദയവായി ചാറ്റിൽ നേരിട്ട് നൽകരുത്.",
            "steps": ["സന്ദേശത്തിൽ നിന്നും ഒടിപി അല്ലെങ്കിൽ ആധാർ നമ്പർ ഒഴിവാക്കി വീണ്ടും ചോദിക്കുക."],
            "warnings": ["വ്യക്തിഗത വിവരങ്ങൾ ക്ലൗഡ് മോഡലിലേക്ക് അയക്കുന്നത് തടഞ്ഞു."],
            "source_refs": [],
            "needs_human_help": False,
            "follow_up_question": "സ്വകാര്യ വിവരങ്ങൾ ഒഴിവാക്കി ചോദ്യം വീണ്ടും ചോദിക്കാമോ?",
        }
    return {
        "language": "en",
        "module": module,
        "reply": "To protect your personal privacy, please do not include sensitive information like your Aadhaar number, OTP, or passwords in your message.",
        "steps": ["Remove any OTP, PIN, or Aadhaar number from your request and try again."],
        "warnings": ["Request contained sensitive personal credentials and was sanitized for safety."],
        "source_refs": [],
        "needs_human_help": False,
        "follow_up_question": "Would you like to ask your question without sharing personal credentials?",
    }


def _build_unavailable_fallback(module: str, language: str, reason: str = "") -> Dict[str, Any]:
    """Fallback response when the AI provider is unreachable or returns unrepairable output."""
    if language == "ml":
        return {
            "language": "ml",
            "module": module,
            "reply": "എഐ സഹായ സേവനം ഇപ്പോൾ ലഭ്യമല്ല. ദയവായി അല്പം കഴിഞ്ഞ് വീണ്ടും ശ്രമിക്കുക അല്ലെങ്കിൽ വിശ്വസ്തനായ ഒരാളുടെ സഹായം തേടുക.",
            "steps": [
                "കുറച്ച് സമയത്തിന് ശേഷം വീണ്ടും ശ്രമിക്കുക.",
                "അടിയന്തിരമാണെങ്കിൽ കുടുംബാംഗവുമായോ വാർഡ് പ്രതിനിധിയുമായോ ബന്ധപ്പെടുക."
            ],
            "warnings": ["എഐ സേവനവുമായി ബന്ധപ്പെടാൻ സാധിക്കുന്നില്ല."],
            "source_refs": [],
            "needs_human_help": True,
            "follow_up_question": None,
        }
    return {
        "language": "en",
        "module": module,
        "reply": "The AI assistant is temporarily unavailable. Please try again shortly or reach out to a trusted helper.",
        "steps": [
            "Wait a moment and try your request again.",
            "Contact a trusted family member or local volunteer if your need is urgent."
        ],
        "warnings": ["AI service connectivity is currently unavailable."],
        "source_refs": [],
        "needs_human_help": True,
        "follow_up_question": None,
    }


def generate_assistance(
    user_text: str,
    module: str,
    language: str,
    verified_context: Optional[List[Any]] = None,
    prepared_image: Optional[Any] = None,
    config: Optional[AIServiceConfig] = None,
) -> Dict[str, Any]:
    """
    Main AI service entrypoint for Member 4 integration.

    Parameters:
    - user_text: required non-empty text, such as a question or extracted message.
    - module: one of 'government_services', 'everyday_tasks', 'digital_safety',
              'family_support', or 'human_help'.
    - language: 'ml' for Malayalam or 'en' for English.
    - verified_context: optional list of trusted excerpts. Each excerpt must include
                        a source identifier and text.
    - prepared_image: optional image data (PIL Image, bytes, base64 dict).

    Returns:
    A validated dictionary strictly matching the contract:
    {
      "language": "ml | en",
      "module": "government_services | everyday_tasks | digital_safety | family_support | human_help",
      "reply": "Short, accessible answer in the requested language",
      "steps": ["Optional ordered action"],
      "warnings": ["Optional safety or uncertainty warning"],
      "source_refs": ["IDs of supplied verified excerpts actually used"],
      "needs_human_help": false,
      "follow_up_question": null
    }
    """
    # 1. Normalize parameters
    norm_lang = _normalize_language(language)
    norm_mod = _normalize_module(module)

    # 2. Handle empty or whitespace input gracefully
    if not user_text or not str(user_text).strip():
        fallback = _build_empty_input_fallback(norm_mod, norm_lang)
        return sanitize_response(fallback, set(), norm_lang, norm_mod).to_contract_dict()

    raw_clean_text = str(user_text).strip()

    # 3. Privacy Boundary: Mask PII locally before cloud forwarding
    cloud_safe_text, privacy_notices = mask_pii_for_cloud(raw_clean_text)

    # Backend validation check
    is_compliant, violations = validate_privacy_compliance(cloud_safe_text)
    if not is_compliant:
        logger.warning("Privacy validation failed for input: %s", violations)
        fallback = _build_privacy_rejected_fallback(norm_mod, norm_lang, ", ".join(violations))
        return sanitize_response(fallback, set(), norm_lang, norm_mod, privacy_notices).to_contract_dict()

    # 4. Normalize verified context and build valid source ID set
    normalized_context = _normalize_verified_context(verified_context)
    valid_source_ids: Set[str] = {v.id for v in normalized_context}

    # 5. Resolve configuration
    cfg = config or AIServiceConfig.from_env()

    # 6. Dispatch to appropriate provider
    raw_result: Optional[Dict[str, Any]] = None

    try:
        if cfg.has_gemini:
            provider = GeminiProvider(
                api_key=cfg.gemini_api_key,  # type: ignore
                model_name=cfg.gemini_model,
                timeout_seconds=cfg.timeout_seconds,
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    provider.generate,
                    cloud_safe_text,
                    norm_mod,
                    norm_lang,
                    normalized_context,
                    prepared_image,
                )
                raw_result = future.result(timeout=cfg.timeout_seconds)

        elif cfg.has_openai:
            provider = OpenAIProvider(
                api_key=cfg.openai_api_key,  # type: ignore
                model_name=cfg.openai_model,
                timeout_seconds=cfg.timeout_seconds,
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    provider.generate,
                    cloud_safe_text,
                    norm_mod,
                    norm_lang,
                    normalized_context,
                    prepared_image,
                )
                raw_result = future.result(timeout=cfg.timeout_seconds)

        elif cfg.allow_mock_fallback:
            mock = MockProvider()
            raw_result = mock.generate(
                user_text=cloud_safe_text,
                module=norm_mod,
                language=norm_lang,
                verified_context=normalized_context,
            )

        else:
            logger.warning("No LLM API key configured and mock fallback is disabled.")
            raw_result = _build_unavailable_fallback(norm_mod, norm_lang, "No provider configured")

    except concurrent.futures.TimeoutError:
        logger.error("AI service call timed out after %s seconds", cfg.timeout_seconds)
        raw_result = _build_unavailable_fallback(norm_mod, norm_lang, "Timeout")
    except Exception as exc:
        logger.error("Provider execution failed: %s", str(exc)[:80])
        raw_result = _build_unavailable_fallback(norm_mod, norm_lang, "Provider error")

    # 7. Fallback if provider returned None or invalid structure
    if not isinstance(raw_result, dict):
        raw_result = _build_unavailable_fallback(norm_mod, norm_lang, "Invalid response")

    # 8. Validate and sanitize against the response contract
    response = sanitize_response(
        data=raw_result,
        valid_source_ids=valid_source_ids,
        expected_language=norm_lang,
        expected_module=norm_mod,
        privacy_notices=privacy_notices,
    )

    return response.to_contract_dict()


"""
OpenAI provider implementation for teams configuring OPENAI_API_KEY.
"""

import logging
from typing import Any, Dict, List, Optional

from ..parser import extract_and_parse_json
from ..privacy import safe_summary_for_logs
from ..prompts import SYSTEM_PROMPT, build_user_prompt
from ..schemas import VerifiedExcerpt

logger = logging.getLogger("ai_service.openai")


class OpenAIProvider:
    """Invokes OpenAI Chat Completions with JSON mode."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini", timeout_seconds: float = 15.0):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)

    def generate(
        self,
        user_text: str,
        module: str,
        language: str,
        verified_context: Optional[List[VerifiedExcerpt]] = None,
        prepared_image: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        user_prompt = build_user_prompt(
            user_text=user_text,
            module=module,
            language=language,
            verified_context=verified_context,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        logger.info(
            "Calling OpenAI (model=%s, module=%s, lang=%s, input=%s)",
            self.model_name,
            module,
            language,
            safe_summary_for_logs(user_text),
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        raw_text = response.choices[0].message.content or ""
        return extract_and_parse_json(raw_text)


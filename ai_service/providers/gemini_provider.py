"""
Google Gemini provider implementation using the official google-genai SDK.
"""

import base64
import io
import logging
from typing import Any, Dict, List, Optional

from ..parser import extract_and_parse_json
from ..privacy import safe_summary_for_logs
from ..prompts import SYSTEM_PROMPT, build_user_prompt
from ..schemas import VerifiedExcerpt

logger = logging.getLogger("ai_service.gemini")


class GeminiProvider:
    """Invokes Google Gemini with structured JSON output and safety constraints."""

    def __init__(self, api_key: str, model_name: str = "gemini-3.8-flash", timeout_seconds: float = 15.0):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

        from google import genai
        self.client = genai.Client(api_key=api_key)

    def _prepare_image_part(self, prepared_image: Any) -> Optional[Any]:
        """Safely transforms prepared_image into a google.genai Part object."""
        if prepared_image is None:
            return None

        from google.genai import types

        try:
            # Case 1: PIL Image
            if hasattr(prepared_image, "save"):
                buf = io.BytesIO()
                fmt = getattr(prepared_image, "format", None) or "JPEG"
                prepared_image.save(buf, format=fmt)
                mime = f"image/{fmt.lower()}"
                return types.Part.from_bytes(data=buf.getvalue(), mime_type=mime)

            # Case 2: Raw bytes
            if isinstance(prepared_image, (bytes, bytearray)):
                return types.Part.from_bytes(data=bytes(prepared_image), mime_type="image/jpeg")

            # Case 3: Dictionary with data / mime_type
            if isinstance(prepared_image, dict):
                data = prepared_image.get("data")
                mime = prepared_image.get("mime_type", "image/jpeg")
                if isinstance(data, str):
                    raw_bytes = base64.b64decode(data)
                elif isinstance(data, (bytes, bytearray)):
                    raw_bytes = bytes(data)
                else:
                    return None
                return types.Part.from_bytes(data=raw_bytes, mime_type=mime)

        except Exception as e:
            logger.warning("Failed to process prepared_image for Gemini: %s", str(e))

        return None

    def generate(
        self,
        user_text: str,
        module: str,
        language: str,
        verified_context: Optional[List[VerifiedExcerpt]] = None,
        prepared_image: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """Calls Gemini API and returns the parsed JSON response dictionary."""
        from google.genai import types

        user_prompt = build_user_prompt(
            user_text=user_text,
            module=module,
            language=language,
            verified_context=verified_context,
        )

        contents: List[Any] = [user_prompt]

        # Add image if provided
        image_part = self._prepare_image_part(prepared_image)
        if image_part is not None:
            contents.append(image_part)

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2,
        )

        logger.info(
            "Calling Gemini (model=%s, module=%s, lang=%s, input=%s)",
            self.model_name,
            module,
            language,
            safe_summary_for_logs(user_text),
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        raw_text = getattr(response, "text", "") or ""
        return extract_and_parse_json(raw_text)


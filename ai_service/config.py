"""
Configuration management for the AI Assistance Service.
Reads environment variables securely without exposing secrets.
"""

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class AIServiceConfig:
    """Immutable configuration container for AI service calls."""
    gemini_api_key: Optional[str]
    gemini_model: str
    openai_api_key: Optional[str]
    openai_model: str
    timeout_seconds: float
    allow_mock_fallback: bool

    @classmethod
    def from_env(cls) -> "AIServiceConfig":
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        try:
            timeout = float(os.getenv("AI_SERVICE_TIMEOUT_SECONDS", "30.0"))
        except ValueError:
            timeout = 30.0

        mock_env = os.getenv("AI_SERVICE_MOCK_FALLBACK", "").strip().lower()
        if mock_env in ("true", "1", "yes"):
            allow_mock = True
        elif mock_env in ("false", "0", "no"):
            allow_mock = False
        else:
            allow_mock = not bool(gemini_key or openai_key)

        return cls(
            gemini_api_key=gemini_key,
            gemini_model=gemini_model,
            openai_api_key=openai_key,
            openai_model=openai_model,
            timeout_seconds=timeout,
            allow_mock_fallback=allow_mock,
        )

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())


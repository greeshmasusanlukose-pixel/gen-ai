"""
AI Assistance Service package for Kerala Accessibility Assistant.
Member 3 implementation for 4-hour hackathon MVP.
"""

from .config import AIServiceConfig
from .privacy import mask_pii_for_cloud, validate_privacy_compliance
from .schemas import (
    ALLOWED_LANGUAGES,
    ALLOWED_MODULES,
    AssistanceModule,
    AssistanceResponse,
    SupportedLanguage,
    VerifiedExcerpt,
)
from .service import generate_assistance

__all__ = [
    "generate_assistance",
    "AssistanceResponse",
    "AssistanceModule",
    "SupportedLanguage",
    "VerifiedExcerpt",
    "AIServiceConfig",
    "mask_pii_for_cloud",
    "validate_privacy_compliance",
    "ALLOWED_LANGUAGES",
    "ALLOWED_MODULES",
]


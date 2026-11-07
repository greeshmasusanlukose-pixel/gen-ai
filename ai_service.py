"""
AI Service top-level export and interface for Member 4 backend integration.
Usage:
    from ai_service import generate_assistance
"""

from ai_service.config import AIServiceConfig
from ai_service.privacy import mask_pii_for_cloud, validate_privacy_compliance
from ai_service.schemas import (
    ALLOWED_LANGUAGES,
    ALLOWED_MODULES,
    AssistanceModule,
    AssistanceResponse,
    SupportedLanguage,
    VerifiedExcerpt,
)
from ai_service.service import generate_assistance

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


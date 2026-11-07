"""
Pydantic schemas and contract definitions for the AI Assistance Service.
Member 3: AI/LLM Service implementation for Kerala Accessibility Assistant.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssistanceModule(str, Enum):
    GOVERNMENT_SERVICES = "government_services"
    EVERYDAY_TASKS = "everyday_tasks"
    DIGITAL_SAFETY = "digital_safety"
    FAMILY_SUPPORT = "family_support"
    HUMAN_HELP = "human_help"


class SupportedLanguage(str, Enum):
    MALAYALAM = "ml"
    ENGLISH = "en"


ALLOWED_MODULES = {
    "government_services",
    "everyday_tasks",
    "digital_safety",
    "family_support",
    "human_help",
}

ALLOWED_LANGUAGES = {"ml", "en"}


class VerifiedExcerpt(BaseModel):
    """A verified knowledge snippet supplied by the application."""
    id: str
    text: str
    title: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class AssistanceResponse(BaseModel):
    """
    Strict response contract required by Member 4:
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
    language: Literal["ml", "en"]
    module: Literal[
        "government_services",
        "everyday_tasks",
        "digital_safety",
        "family_support",
        "human_help",
    ]
    reply: str
    steps: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list)
    needs_human_help: bool = False
    follow_up_question: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("steps", "warnings", "source_refs", mode="before")
    @classmethod
    def ensure_list_of_strings(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            stripped = v.strip()
            return [stripped] if stripped else []
        if isinstance(v, (list, tuple)):
            return [str(item).strip() for item in v if item is not None and str(item).strip()]
        return []

    @field_validator("follow_up_question", mode="before")
    @classmethod
    def clean_follow_up(cls, v: Any) -> Optional[str]:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return str(v).strip()

    def to_contract_dict(self) -> Dict[str, Any]:
        """Return exactly the dictionary structure agreed in the response contract."""
        return {
            "language": self.language,
            "module": self.module,
            "reply": self.reply,
            "steps": list(self.steps),
            "warnings": list(self.warnings),
            "source_refs": list(self.source_refs),
            "needs_human_help": bool(self.needs_human_help),
            "follow_up_question": self.follow_up_question,
        }


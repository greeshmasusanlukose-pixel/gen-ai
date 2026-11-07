from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.database.base import Base, TimestampMixin, generate_uuid


class GovernmentScheme(Base, TimestampMixin):
    __tablename__ = "government_schemes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. "kerala-old-age-pension"
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_ml: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Senior Citizen, Disability, Healthcare, etc.
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_ml: Mapped[str] = mapped_column(Text, nullable=False)
    eligibility_criteria: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array or structured text
    benefits: Mapped[str] = mapped_column(Text, nullable=False)  # Benefits details
    required_documents: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array or list of required docs
    application_procedure: Mapped[str] = mapped_column(Text, nullable=False)  # Step-by-step guidance
    official_portal_url: Mapped[str] = mapped_column(String(500), nullable=False)
    department: Mapped[str] = mapped_column(String(200), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified_source_reference: Mapped[str] = mapped_column(String(300), nullable=False)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database.base import Base, TimestampMixin, generate_uuid


class UserConsent(Base, TimestampMixin):
    __tablename__ = "user_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    grantee_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # Specific FamilyMember ID or None for general
    grantee_type: Mapped[str] = mapped_column(String(30), default="family_member", nullable=False)  # family_member, emergency, helper
    scope: Mapped[str] = mapped_column(String(50), nullable=False)  # view_activity, view_documents, medical_info, manage_requests
    is_granted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="consents")

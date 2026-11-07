from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Integer, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database.base import Base, TimestampMixin, generate_uuid


class Helper(Base, TimestampMixin):
    __tablename__ = "helpers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    panchayat_or_locality: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="Volunteer", nullable=False)  # Volunteer, Kudumbashree, NSS, Caregiver
    skills: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list of skills
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verification_badge: Mapped[str] = mapped_column(String(100), default="Kudumbashree Verified", nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=4.9, nullable=False)
    completed_tasks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    assigned_requests = relationship("AssistanceRequest", back_populates="helper")


class AssistanceRequest(Base, TimestampMixin):
    __tablename__ = "assistance_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # Mobility, Medical, Govt Escort, Tech Support, Daily Essentials
    urgency: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, emergency
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)  # open, assigned, in_progress, resolved, cancelled
    assigned_helper_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("helpers.id", ondelete="SET NULL"), nullable=True)
    district: Mapped[str] = mapped_column(String(50), nullable=False)
    location_details: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(10), default="ml", nullable=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user_feedback_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user = relationship("User", back_populates="assistance_requests")
    helper = relationship("Helper", back_populates="assigned_requests")

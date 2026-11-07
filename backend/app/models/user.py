from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.database.base import Base, TimestampMixin, generate_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="ml", nullable=False)
    district: Mapped[str] = mapped_column(String(50), default="Thiruvananthapuram", nullable=False)
    panchayat_or_municipality: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_senior_citizen: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_differently_abled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    disability_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    accessibility_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    family_members = relationship("FamilyMember", back_populates="user", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="user", cascade="all, delete-orphan")
    consents = relationship("UserConsent", back_populates="user", cascade="all, delete-orphan")
    assistance_requests = relationship("AssistanceRequest", back_populates="user", cascade="all, delete-orphan")

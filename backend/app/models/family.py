from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database.base import Base, TimestampMixin, generate_uuid


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)  # Son, Daughter, Caregiver, etc.
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary_caregiver: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_view_activity: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_requests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="family_members")


class EmergencyContact(Base, TimestampMixin):
    __tablename__ = "emergency_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    priority_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_sos_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="emergency_contacts")

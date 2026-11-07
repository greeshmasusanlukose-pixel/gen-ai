from sqlalchemy import String, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from app.database.base import Base, TimestampMixin, generate_uuid


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), default="New Conversation", nullable=False)
    primary_language: Mapped[str] = mapped_column(String(10), default="ml", nullable=False)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    files = relationship("UploadedFile", back_populates="conversation")


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ml", nullable=False)
    has_voice_audio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    audio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    detected_intent: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON for structured tags, risk flags, etc.

    conversation = relationship("Conversation", back_populates="messages")


class UploadedFile(Base, TimestampMixin):
    __tablename__ = "uploaded_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_category: Mapped[str] = mapped_column(String(20), nullable=False)  # image, document, audio
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    processed_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Extracted OCR/transcription text

    conversation = relationship("Conversation", back_populates="files")

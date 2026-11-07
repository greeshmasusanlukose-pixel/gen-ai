from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

def now():
    return datetime.now(timezone.utc)

class Entity:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class User(Entity, Base):
    __tablename__ = 'users'
    name: Mapped[str]
    language: Mapped[str] = mapped_column(default='ml')
    conversations: Mapped[list['Conversation']] = relationship(back_populates='user')

class AccessSession(Entity, Base):
    __tablename__ = 'access_sessions'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Conversation(Entity, Base):
    __tablename__ = 'conversations'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    user: Mapped[User] = relationship(back_populates='conversations')
    messages: Mapped[list['Message']] = relationship(back_populates='conversation', order_by='Message.created_at')

class Message(Entity, Base):
    __tablename__ = 'messages'
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'), index=True)
    role: Mapped[str]
    text: Mapped[str] = mapped_column(Text)
    is_mock: Mapped[bool] = mapped_column(default=False)
    conversation: Mapped[Conversation] = relationship(back_populates='messages')

class UploadedFile(Entity, Base):
    __tablename__ = 'uploaded_files'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    media_type: Mapped[str]
    storage_name: Mapped[str]
    size: Mapped[int]

class FamilyMember(Entity, Base):
    __tablename__ = 'family_members'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    member_user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    relationship_label: Mapped[str]

class EmergencyContact(Entity, Base):
    __tablename__ = 'emergency_contacts'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    name: Mapped[str]
    phone: Mapped[str]

class UserConsent(Entity, Base):
    __tablename__ = 'user_consents'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    family_member_id: Mapped[str] = mapped_column(ForeignKey('family_members.id'), unique=True)
    scope: Mapped[str] = mapped_column(default='assistance')
    granted: Mapped[bool]

class Helper(Entity, Base):
    __tablename__ = 'helpers'
    name: Mapped[str]
    verified: Mapped[bool] = mapped_column(default=False)
    simulated: Mapped[bool] = mapped_column(default=True)
    available: Mapped[bool] = mapped_column(default=True)

class AssistanceRequest(Entity, Base):
    __tablename__ = 'assistance_requests'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'), index=True)
    category: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(default='pending', index=True)
    helper_id: Mapped[str | None] = mapped_column(ForeignKey('helpers.id'))
    family_member_id: Mapped[str | None] = mapped_column(ForeignKey('family_members.id'))
    resolution: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class GovernmentScheme(Entity, Base):
    __tablename__ = 'government_schemes'
    title: Mapped[str] = mapped_column(index=True)
    language: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    eligibility: Mapped[list] = mapped_column(JSON)
    benefits: Mapped[list] = mapped_column(JSON)
    documents: Mapped[list] = mapped_column(JSON)
    procedure: Mapped[list] = mapped_column(JSON)
    source_url: Mapped[str]
    verified_at: Mapped[str]
    verified: Mapped[bool] = mapped_column(default=False)

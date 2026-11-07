from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, HttpUrl

Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=8000)]
Language = Literal['ml', 'en', 'auto']

class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

class UserIn(Schema):
    name: Short
    language: Literal['ml', 'en'] = 'ml'

class UserOut(UserIn):
    id: str

class SessionOut(Schema):
    user: UserOut
    access_token: str
    token_type: str = 'bearer'
    expires_at: datetime

class ChatIn(Schema):
    text: Text
    session_id: str | None = None
    language: Language = 'auto'

class AIResult(Schema):
    text: Text
    steps: list[Short] = Field(default_factory=list, max_length=20)
    language: Literal['ml', 'en']
    is_mock: bool = False

class ChatOut(Schema):
    session_id: str
    answer: AIResult

class MessageOut(Schema):
    id: str
    role: str
    text: str
    is_mock: bool
    created_at: datetime

class HistoryOut(Schema):
    session_id: str
    messages: list[MessageOut]

class UploadOut(Schema):
    file_id: str
    media_type: str
    size: int
    answer: AIResult

class SafetyIn(Schema):
    text: Text
    language: Language = 'auto'

class SafetyOut(Schema):
    risk_level: Literal['low', 'medium', 'high', 'unknown']
    reason: Text
    warning_signs: list[Short] = Field(max_length=20)
    recommended_safe_action: Text
    is_mock: bool = False
    language: Literal['ml', 'en']
    disclaimer: str = 'This assessment does not prove safety / ഈ വിലയിരുത്തൽ സുരക്ഷ ഉറപ്പാക്കുന്നില്ല.'

class ContactIn(Schema):
    name: Short
    phone: Annotated[str, StringConstraints(pattern=r'^\+?[0-9 ()-]{7,20}$')]

class ContactOut(ContactIn):
    id: str

class MemberIn(Schema):
    member_user_id: str
    relationship_label: Short

class MemberOut(MemberIn):
    id: str

class ConsentIn(Schema):
    granted: bool

class ConsentOut(ConsentIn):
    id: str
    family_member_id: str
    scope: str

class HelpIn(Schema):
    category: Literal['government', 'digital', 'daily_living', 'other']
    description: Text

class FamilyHelpIn(HelpIn):
    family_member_id: str

class HelpPatch(Schema):
    status: Literal['assigned', 'in_progress', 'resolved', 'cancelled']
    helper_id: str | None = None
    resolution: Text | None = None

class HelpOut(HelpIn):
    id: str
    status: str
    helper_id: str | None
    family_member_id: str | None
    resolution: str | None
    created_at: datetime
    updated_at: datetime

class HelperOut(Schema):
    id: str
    name: str
    verified: bool
    simulated: bool
    available: bool

class SchemeIn(Schema):
    id: Short
    title: Short
    language: Literal['ml', 'en']
    description: Text
    eligibility: list[Text]
    benefits: list[Text]
    documents: list[Text]
    procedure: list[Text]
    source_url: HttpUrl
    verified_at: datetime
    verified: bool

class SchemeOut(Schema):
    id: str
    title: str
    language: str
    description: str
    eligibility: list[str]
    benefits: list[str]
    documents: list[str]
    procedure: list[str]
    source_url: str
    verified_at: str
    verified: bool

class SchemeList(Schema):
    items: list[SchemeOut]
    message: str

class SpeechIn(Schema):
    text: Text
    language: Literal['ml', 'en'] = 'ml'

class SpeechOut(Schema):
    audio_base64: str = Field(min_length=1, max_length=15000000)
    media_type: Literal['audio/wav', 'audio/mpeg']
    is_mock: bool = False

class HealthOut(Schema):
    status: str
    ai_provider: str

class ErrorDetail(Schema):
    code: str
    message: str
    fields: list[str] | None = None

class ErrorOut(Schema):
    error: ErrorDetail

import base64
from typing import Protocol
import httpx
from pydantic import ValidationError
from app.core.exceptions import AppError
from app.schemas.api import AIResult, SafetyOut, SpeechOut

class AIService(Protocol):
    capabilities: set[str]
    async def chat(self, text, language, history) -> AIResult: ...
    async def image(self, data, media_type, language) -> AIResult: ...
    async def document(self, text, language) -> AIResult: ...
    async def transcribe(self, data, media_type, language) -> AIResult: ...
    async def safety(self, text, language) -> SafetyOut: ...
    async def speak(self, text, language) -> SpeechOut: ...

def require_capability(provider, capability):
    if capability not in provider.capabilities:
        raise AppError(501, 'unsupported_capability', 'Configured AI provider does not support this operation / ഈ സേവനം ലഭ്യമല്ല')

class MockAI:
    capabilities = {'chat', 'image', 'document', 'safety'}
    def answer(self, language):
        return AIResult(text='പരീക്ഷണ മറുപടി: ഇത് യഥാർത്ഥ AI ഉപദേശമല്ല. സഹായത്തിനായി കുടുംബാംഗത്തെയോ സഹായിയെയോ സമീപിക്കുക.' if language == 'ml' else 'Mock response: this is not real AI advice. Ask a family member or helper for assistance.', steps=['സഹായ അഭ്യർത്ഥന നൽകുക'] if language == 'ml' else ['Create an assistance request'], language=language, is_mock=True)
    async def chat(self, text, language, history):
        return self.answer(language)
    async def image(self, data, media_type, language):
        return self.answer(language)
    async def document(self, text, language):
        return self.answer(language)
    async def transcribe(self, data, media_type, language):
        require_capability(self, 'transcribe')
    async def speak(self, text, language):
        require_capability(self, 'speak')
    async def safety(self, text, language):
        risky = any(word in text.lower() for word in ['otp', 'password', 'pin', 'urgent', 'ഒടിപി'])
        ml = language == 'ml'
        return SafetyOut(risk_level='high' if risky else 'unknown', reason=('പരീക്ഷണ നിയമാധിഷ്ഠിത പരിശോധന; സുരക്ഷ ഉറപ്പില്ല.' if ml else 'Mock rule-based screening; safety cannot be established.'), warning_signs=(['രഹസ്യ വിവരമോ അടിയന്തര നടപടിയോ ആവശ്യപ്പെടുന്നു'] if ml else ['Credential or urgency wording']) if risky else [], recommended_safe_action='രഹസ്യ വിവരങ്ങൾ പങ്കിടരുത്. ഔദ്യോഗിക സഹായവുമായി ബന്ധപ്പെടുക.' if ml else 'Do not share credentials or open links. Contact the service through an independently known official channel.', language=language, is_mock=True)

class HTTPAI:
    """Member 3 gateway adapter. The gateway owns provider-specific model calls."""
    def __init__(self, settings, client):
        self.settings, self.client = settings, client
        self.capabilities = set(settings.AI_CAPABILITIES)
    async def call(self, operation, payload, schema=AIResult):
        require_capability(self, operation)
        try:
            response = await self.client.post(self.settings.AI_BASE_URL.rstrip('/') + '/' + operation, json={**payload, 'model': self.settings.AI_MODEL}, headers={'Authorization': f'Bearer {self.settings.AI_API_KEY}'} if self.settings.AI_API_KEY else {})
            response.raise_for_status()
            if len(response.content) > 16000000:
                raise ValueError('oversized response')
            return schema.model_validate(response.json())
        except (httpx.HTTPError, ValidationError, ValueError):
            raise AppError(503, 'ai_unavailable', 'AI service unavailable; please try again / AI സേവനം ഇപ്പോൾ ലഭ്യമല്ല') from None
    async def chat(self, text, language, history):
        return await self.call('chat', dict(text=text, language=language, history=history))
    async def image(self, data, media_type, language):
        return await self.call('image', dict(data_base64=base64.b64encode(data).decode(), media_type=media_type, language=language))
    async def document(self, text, language):
        return await self.call('document', dict(text=text, language=language))
    async def transcribe(self, data, media_type, language):
        return await self.call('transcribe', dict(data_base64=base64.b64encode(data).decode(), media_type=media_type, language=language))
    async def safety(self, text, language):
        return await self.call('safety', dict(text=text, language=language), SafetyOut)
    async def speak(self, text, language):
        return await self.call('speak', dict(text=text, language=language), SpeechOut)

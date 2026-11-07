import httpx
import pytest
from sqlalchemy import select, func
from app.services.ai_service import HTTPAI
from app.models.entities import Message, Conversation

def install_gateway(client, handler):
    settings = client.app.state.settings.model_copy(update={'AI_CAPABILITIES': ['chat', 'safety', 'image', 'document', 'transcribe', 'speak']})
    gateway = HTTPAI(settings, httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    client.app.state.ai = gateway

def test_http_gateway_contract_and_history(client, identity):
    calls = []
    def handler(request):
        import json
        calls.append(json.loads(request.content))
        assert request.url.path == '/chat'
        return httpx.Response(200, json={'text': 'മറുപടി', 'steps': [], 'language': 'ml', 'is_mock': False})
    install_gateway(client, handler)
    first = client.post('/api/assistant/chat', headers=identity[1], json={'text': 'സഹായം വേണം'}).json()
    assert first['answer']['is_mock'] is False
    assert client.post('/api/assistant/chat', headers=identity[1], json={'text': 'വീണ്ടും', 'session_id': first['session_id']}).status_code == 200
    assert len(calls[1]['history']) == 2

@pytest.mark.parametrize('mode', ['timeout', 'http_error', 'invalid_json', 'invalid_schema'])
def test_provider_failure_is_sanitized_and_atomic(client, identity, mode):
    def handler(request):
        if mode == 'timeout':
            raise httpx.ReadTimeout('private upstream details', request=request)
        if mode == 'http_error':
            return httpx.Response(500, text='private upstream details')
        if mode == 'invalid_json':
            return httpx.Response(200, text='private upstream details')
        return httpx.Response(200, json={'unexpected': 'private upstream details'})
    install_gateway(client, handler)
    response = client.post('/api/assistant/chat', headers=identity[1], json={'text': 'hello'})
    assert response.status_code == 503
    assert 'private upstream' not in response.text
    with client.app.state.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Message)) == 0
        assert db.scalar(select(func.count()).select_from(Conversation)) == 0

def test_gateway_document_image_voice_and_safety(client, identity):
    import json
    import base64
    import wave
    from io import BytesIO
    from PIL import Image
    calls = []
    def handler(request):
        payload = json.loads(request.content)
        calls.append(request.url.path)
        assert payload['language'] == 'ml'
        if request.url.path == '/speak':
            return httpx.Response(200, json={'audio_base64': base64.b64encode(b'test fixture').decode(), 'media_type': 'audio/wav'})
        if request.url.path == '/safety':
            return httpx.Response(200, json={'risk_level': 'unknown', 'reason': 'പരിശോധിക്കുക', 'warning_signs': [], 'recommended_safe_action': 'സഹായം തേടുക', 'language': 'ml'})
        if request.url.path in ['/image', '/transcribe']:
            assert base64.b64decode(payload['data_base64'])
        return httpx.Response(200, json={'text': 'മറുപടി', 'steps': [], 'language': 'ml'})
    install_gateway(client, handler)
    headers = identity[1]
    assert client.post('/api/assistant/upload', headers=headers, files={'file': ('test.txt', 'സഹായം'.encode())}).status_code == 201
    picture = BytesIO()
    Image.new('RGB', (2, 2)).save(picture, format='PNG')
    assert client.post('/api/assistant/upload', headers=headers, files={'file': ('test.png', picture.getvalue())}).status_code == 201
    audio = BytesIO()
    with wave.open(audio, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b'\x00\x00' * 80)
    assert client.post('/api/assistant/upload', headers=headers, files={'file': ('test.wav', audio.getvalue())}).status_code == 201
    assert client.post('/api/assistant/speech', headers=headers, json={'text': 'നമസ്കാരം'}).status_code == 200
    assert client.post('/api/guardian/analyze', headers=headers, json={'text': 'സഹായം വേണം'}).status_code == 200
    assert calls == ['/document', '/image', '/transcribe', '/speak', '/safety']

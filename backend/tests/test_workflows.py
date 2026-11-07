from io import BytesIO
import wave
import pytest
from PIL import Image
from sqlalchemy import select, func, inspect
from app.models.entities import Message, Conversation, GovernmentScheme, UploadedFile
from conftest import register

def test_startup_and_database(client):
    root = client.get('/', follow_redirects=False)
    assert root.status_code == 307
    assert root.headers['location'] == 'docs'
    assert client.get('/health').json()['status'] == 'ok'
    with client.app.state.sessions() as db:
        assert len(inspect(db.bind).get_table_names()) == 11
    assert client.get('/openapi.json').status_code == 200
    assert client.get('/docs').status_code == 200

def test_malayalam_end_to_end(client, identity):
    user, headers = identity
    response = client.post('/api/assistant/chat', headers=headers, json={'text': 'പെൻഷൻ അപേക്ഷിക്കാൻ സഹായിക്കാമോ?'})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['answer']['is_mock'] is True
    assert data['answer']['language'] == 'ml'
    assert 'പരീക്ഷണ' in data['answer']['text']
    history = client.get('/api/assistant/history/' + data['session_id'], headers=headers).json()
    assert len(history['messages']) == 2
    assert history['messages'][0]['text'] == 'പെൻഷൻ അപേക്ഷിക്കാൻ സഹായിക്കാമോ?'
    assert client.post('/api/assistant/chat', headers=headers, json={'text': 'അടുത്ത നടപടി?', 'session_id': data['session_id']}).status_code == 200
    _, other = register(client, 'Family')
    assert client.get('/api/assistant/history/' + data['session_id'], headers=other).status_code == 404
    assert client.post('/api/assistant/chat', headers=other, json={'text': 'hello', 'session_id': data['session_id']}).status_code == 404
    with client.app.state.sessions() as db:
        assert db.scalar(select(func.count()).select_from(Message)) == 4

@pytest.mark.parametrize('payload', [{}, {'text': ''}, {'text': 'a' * 8001}, {'text': 'hello', 'unexpected': True}, {'text': 'OTP: 123456'}, {'text': 'password is private-value'}])
def test_invalid_requests(client, identity, payload):
    response = client.post('/api/assistant/chat', headers=identity[1], json=payload)
    assert response.status_code == 422
    assert '123456' not in response.text and 'private-value' not in response.text

def test_auth_and_logout(client, identity):
    assert client.get('/api/family/contacts').status_code == 401
    assert client.get('/api/users/me', headers={'Authorization': 'Bearer invalid'}).status_code == 401
    assert client.delete('/api/users/sessions', headers=identity[1]).status_code == 204
    assert client.get('/api/users/me', headers=identity[1]).status_code == 401

def test_uploads(client, identity):
    headers = identity[1]
    response = client.post('/api/assistant/upload', headers=headers, files={'file': ('../../private.txt', 'സഹായം വേണം'.encode(), 'text/plain')})
    assert response.status_code == 201, response.text
    assert response.json()['answer']['is_mock']
    image = BytesIO()
    Image.new('RGB', (8, 8)).save(image, format='PNG')
    assert client.post('/api/assistant/upload', headers=headers, files={'file': ('image.png', image.getvalue(), 'image/png')}).status_code == 201
    with client.app.state.sessions() as db:
        assert all(f.storage_name == 'not-retained' for f in db.scalars(select(UploadedFile)))

@pytest.mark.parametrize('name,content,status', [('bad.exe', b'MZ', 415), ('bad.png', b'fake image', 422), ('bad.pdf', b'not pdf', 422), ('empty.txt', b'', 413), ('big.txt', b'x' * (1024 * 1024 + 1), 413), ('secret.txt', b'OTP: 123456', 422)])
def test_invalid_uploads(client, identity, name, content, status):
    assert client.post('/api/assistant/upload', headers=identity[1], files={'file': (name, content)}).status_code == status

def test_voice_explicitly_unsupported(client, identity):
    audio = BytesIO()
    with wave.open(audio, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b'\x00\x00' * 800)
    assert client.post('/api/assistant/upload', headers=identity[1], files={'file': ('voice.wav', audio.getvalue())}).status_code == 501
    assert client.post('/api/assistant/speech', headers=identity[1], json={'text': 'നമസ്കാരം'}).status_code == 501

def test_government_empty_and_verified_retrieval(client):
    assert client.get('/api/government/schemes').json()['items'] == []
    # Synthetic test-only records, never shipped as actual scheme information.
    with client.app.state.sessions.begin() as db:
        for verified in [True, False]:
            db.add(GovernmentScheme(id=str(verified), title='Test catalogue fixture', language='en', description='Synthetic test data', eligibility=[], benefits=[], documents=[], procedure=[], source_url='https://example.org/test', verified_at='2026-01-01T00:00:00Z', verified=verified))
    items = client.get('/api/government/schemes?q=fixture').json()['items']
    assert len(items) == 1 and items[0]['verified']
    assert client.get('/api/government/schemes/True').status_code == 200
    assert client.get('/api/government/schemes/False').status_code == 404
    assert client.get('/api/government/schemes/missing').status_code == 404

def test_guardian(client, identity):
    result = client.post('/api/guardian/analyze', headers=identity[1], json={'text': 'Please share your OTP urgently at https://suspicious.invalid'}).json()
    assert result['risk_level'] == 'high' and result['is_mock']
    assert result['disclaimer']
    result = client.post('/api/guardian/analyze', headers=identity[1], json={'text': 'hello'}).json()
    assert result['risk_level'] == 'unknown'

def test_family_consent_revocation_and_privacy(client, identity):
    owner, headers = identity
    relative, family_headers = register(client, 'Relative')
    contact = client.post('/api/family/contacts', headers=headers, json={'name': 'Relative', 'phone': '+91 9876543210'})
    assert contact.status_code == 201
    assert client.get('/api/family/contacts', headers=family_headers).json() == []
    member = client.post('/api/family/members', headers=headers, json={'member_user_id': relative['id'], 'relationship_label': 'daughter'}).json()
    consent_url = '/api/family/members/' + member['id'] + '/consent'
    payload = {'category': 'digital', 'description': 'Help using my phone', 'family_member_id': member['id']}
    assert client.post('/api/family/assistance', headers=headers, json=payload).status_code == 403
    assert client.put(consent_url, headers=family_headers, json={'granted': True}).status_code == 404
    assert client.put(consent_url, headers=headers, json={'granted': True}).status_code == 200
    result = client.post('/api/family/assistance', headers=headers, json=payload)
    assert result.status_code == 201
    assert len(client.get('/api/family/assistance/inbox', headers=family_headers).json()) == 1
    assert client.get('/api/human-help/requests/' + result.json()['id'], headers=family_headers).status_code == 404
    assert client.put(consent_url, headers=headers, json={'granted': False}).status_code == 200
    assert client.get('/api/family/assistance/inbox', headers=family_headers).json() == []
    assert client.delete('/api/family/contacts/' + contact.json()['id'], headers=headers).status_code == 204

def test_help_workflow(client, identity):
    headers = identity[1]
    result = client.post('/api/human-help/requests', headers=headers, json={'category': 'government', 'description': 'Help submitting a form'})
    assert result.status_code == 201
    url = '/api/human-help/requests/' + result.json()['id']
    assert client.patch(url, headers=headers, json={'status': 'resolved', 'resolution': 'done'}).status_code == 409
    assert client.patch(url, headers=headers, json={'status': 'assigned', 'helper_id': 'missing'}).status_code == 422
    helper = client.get('/api/human-help/helpers', headers=headers).json()[0]
    assert helper['simulated'] is True
    assert client.patch(url, headers=headers, json={'status': 'assigned', 'helper_id': helper['id']}).status_code == 200
    assert client.patch(url, headers=headers, json={'status': 'in_progress'}).status_code == 200
    assert client.patch(url, headers=headers, json={'status': 'resolved'}).status_code == 422
    assert client.patch(url, headers=headers, json={'status': 'resolved', 'resolution': 'Form completed together'}).status_code == 200
    assert client.get(url, headers=headers).json()['resolution'] == 'Form completed together'
    _, other = register(client)
    assert client.patch(url, headers=other, json={'status': 'cancelled'}).status_code == 404

def test_cors_and_body_limit(client):
    response = client.options('/api/assistant/chat', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'authorization'})
    assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
    assert client.post('/api/users', content=b'x' * (1024 * 1024 + 65537)).status_code == 413

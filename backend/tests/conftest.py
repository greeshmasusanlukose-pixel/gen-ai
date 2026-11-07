import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import Settings

@pytest.fixture
def client(tmp_path):
    settings = Settings(_env_file=None, DATABASE_URL=f'sqlite:///{tmp_path / "test.db"}', SCHEMES_FILE=tmp_path / 'schemes.json', MAX_UPLOAD_SIZE_MB=1)
    with TestClient(create_app(settings)) as client:
        yield client

def register(client, name='അമ്മ'):
    response = client.post('/api/users', json={'name': name, 'language': 'ml'})
    assert response.status_code == 201, response.text
    data = response.json()
    return data['user'], {'Authorization': 'Bearer ' + data['access_token']}

@pytest.fixture
def identity(client):
    return register(client)

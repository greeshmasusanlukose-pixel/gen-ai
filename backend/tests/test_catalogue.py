import json
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import Settings

def test_catalogue_initialization_and_idempotence(tmp_path):
    path = tmp_path / 'schemes.json'
    # Test-only synthetic fixture, not a government claim.
    path.write_text(json.dumps([dict(id='fixture', title='Fixture', language='en', description='Synthetic fixture', eligibility=[], benefits=[], documents=[], procedure=[], source_url='https://example.org/test', verified_at='2026-01-01T00:00:00Z', verified=True)]), encoding='utf-8')
    settings = Settings(_env_file=None, DATABASE_URL=f'sqlite:///{tmp_path / "catalogue.db"}', SCHEMES_FILE=path)
    for _ in range(2):
        with TestClient(create_app(settings)) as client:
            assert len(client.get('/api/government/schemes').json()['items']) == 1

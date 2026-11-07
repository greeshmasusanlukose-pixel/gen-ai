"""Run the actual ASGI server on loopback and exercise a persisted chat."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import httpx

def test_live_uvicorn(tmp_path):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, DATABASE_URL=f'sqlite:///{tmp_path / "live.db"}', AI_PROVIDER='mock', SCHEMES_FILE=str(tmp_path / 'absent.json'))
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(port), '--no-access-log'], cwd=Path(__file__).resolve().parents[1], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    try:
        with httpx.Client(base_url=f'http://127.0.0.1:{port}', timeout=2, trust_env=False) as client:
            deadline = time.monotonic() + 20
            while True:
                assert process.poll() is None, 'Uvicorn exited before readiness'
                try:
                    if client.get('/health').status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                assert time.monotonic() < deadline, 'Server startup timed out'
                time.sleep(0.1)
            session = client.post('/api/users', json={'name': 'അമ്മ'}).json()
            headers = {'Authorization': 'Bearer ' + session['access_token']}
            response = client.post('/api/assistant/chat', headers=headers, json={'text': 'സഹായം വേണം'})
            assert response.status_code == 200
            assert response.json()['answer']['language'] == 'ml'
            history = client.get('/api/assistant/history/' + response.json()['session_id'], headers=headers)
            assert len(history.json()['messages']) == 2
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

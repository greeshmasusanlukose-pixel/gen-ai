from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
ROOT = Path(__file__).resolve().parents[2]
class Settings(BaseSettings):
    APP_NAME: str = 'Kerala Independence & Accessibility Assistant'
    DATABASE_URL: str = f'sqlite:///{ROOT / "accessibility_assistant.db"}'
    CORS_ORIGINS: list[str] = ['http://localhost:3000', 'http://localhost:5173']
    AI_PROVIDER: Literal['mock', 'http'] = 'mock'
    AI_BASE_URL: str = 'http://localhost:9000'
    AI_API_KEY: str = ''
    AI_MODEL: str = ''
    AI_CAPABILITIES: list[str] = ['chat', 'safety']
    AI_REQUEST_TIMEOUT_SECONDS: float = Field(default=30, gt=0, le=120)
    UPLOAD_DIR: Path = ROOT / 'uploads'
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, ge=1, le=25)
    SESSION_HOURS: int = Field(default=24, ge=1, le=168)
    SEED_DEMO_HELPERS: bool = True
    SCHEMES_FILE: Path = ROOT / 'data' / 'schemes.json'
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')

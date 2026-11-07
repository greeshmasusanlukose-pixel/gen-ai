from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.formparsers import MultiPartParser
from sqlalchemy import select, text
from app.core.config import Settings
from app.core.exceptions import install_handlers
from app.core.middleware import BodyLimit
from app.database.session import Base, database
from app.models.entities import Helper
from app.schemas.api import HealthOut, ErrorOut
from app.services.ai_service import MockAI, HTTPAI
from app.services.government_service import import_catalogue
from app.api.routes import users, assistant, government, guardian, family, human_help

# BodyLimit caps requests at <=25 MiB plus overhead. Keep multipart originals
# in memory instead of Starlette's default temporary-disk spooling.
MultiPartParser.spool_max_size = 26 * 1024 * 1024

def create_app(settings=None, ai=None):
    settings = settings or Settings()
    engine, sessions = database(settings.DATABASE_URL)
    @asynccontextmanager
    async def lifespan(app):
        Base.metadata.create_all(engine)
        with sessions.begin() as db:
            import_catalogue(db, settings.SCHEMES_FILE)
            if settings.SEED_DEMO_HELPERS and db.scalar(select(Helper).where(Helper.id == 'demo-helper')) is None:
                db.add(Helper(id='demo-helper', name='Demo helper / പരീക്ഷണ സഹായി', verified=True, simulated=True, available=True))
        async with httpx.AsyncClient(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS, follow_redirects=False) as client:
            app.state.ai = ai or (MockAI() if settings.AI_PROVIDER == 'mock' else HTTPAI(settings, client))
            yield
        engine.dispose()
    app = FastAPI(title=settings.APP_NAME, version='0.1.0', lifespan=lifespan, responses={code: {'model': ErrorOut} for code in [401, 403, 404, 409, 413, 415, 422, 500, 501, 503]})
    app.state.settings, app.state.sessions = settings, sessions
    install_handlers(app)
    app.add_middleware(BodyLimit, limit=settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 65536)
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=False, allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'], allow_headers=['Authorization', 'Content-Type'])
    for module in [users, assistant, government, guardian, family, human_help]:
        app.include_router(module.router, prefix='/api')
    @app.get('/', include_in_schema=False)
    def index():
        return RedirectResponse(url='docs')

    @app.get('/health', response_model=HealthOut, tags=['Health'])
    def health():
        with engine.connect() as connection:
            connection.execute(text('SELECT 1'))
        return HealthOut(status='ok', ai_provider=settings.AI_PROVIDER)
    return app

app = create_app()

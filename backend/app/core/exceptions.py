from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

class AppError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message

def install_handlers(app):
    @app.exception_handler(AppError)
    async def domain(request, exc):
        return JSONResponse(status_code=exc.status, content={'error': {'code': exc.code, 'message': exc.message}})
    @app.exception_handler(RequestValidationError)
    async def validation(request, exc):
        return JSONResponse(status_code=422, content={'error': {'code': 'validation_error', 'message': 'Invalid request / അസാധുവായ അഭ്യർത്ഥന', 'fields': ['.'.join(map(str, e['loc'])) for e in exc.errors()]}})
    @app.exception_handler(HTTPException)
    async def http(request, exc):
        return JSONResponse(status_code=exc.status_code, content={'error': {'code': 'http_error', 'message': str(exc.detail)}})
    @app.exception_handler(Exception)
    async def unexpected(request, exc):
        return JSONResponse(status_code=500, content={'error': {'code': 'internal_error', 'message': 'Unable to complete request / അഭ്യർത്ഥന പൂർത്തിയാക്കാൻ കഴിഞ്ഞില്ല'}})

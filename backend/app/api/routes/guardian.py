from fastapi import APIRouter, Depends, Request
from app.core.security import current_user, reject_secrets
from app.schemas.api import SafetyIn, SafetyOut
from app.services.language import resolve_language
from app.services.ai_service import require_capability

router = APIRouter(prefix='/guardian', tags=['Digital Guardian'])

@router.post('/analyze', response_model=SafetyOut)
async def analyze(payload: SafetyIn, request: Request, user=Depends(current_user)):
    """Screen redacted suspicious text. Never fetch links or persist submitted text."""
    reject_secrets(payload.text)
    require_capability(request.app.state.ai, 'safety')
    result = await request.app.state.ai.safety(payload.text, resolve_language(payload.text, payload.language, user.language))
    for text in [result.reason, result.recommended_safe_action, *result.warning_signs]:
        reject_secrets(text)
    result.disclaimer = SafetyOut.model_fields['disclaimer'].default
    return result

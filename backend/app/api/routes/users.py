import secrets
from datetime import timedelta
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import delete
from app.database.session import get_db
from app.models.entities import User, AccessSession, now
from app.schemas.api import UserIn, UserOut, SessionOut
from app.repositories.records import add
from app.core.security import current_user, digest, reject_secrets

router = APIRouter(prefix='/users', tags=['Sessions'])

@router.post('', response_model=SessionOut, status_code=201)
def register(payload: UserIn, request: Request, db=Depends(get_db)):
    """Create a demo identity and an expiring bearer session. No password is collected."""
    reject_secrets(payload.name)
    user = add(db, User, **payload.model_dump())
    token = secrets.token_urlsafe(32)
    expiry = now() + timedelta(hours=request.app.state.settings.SESSION_HOURS)
    add(db, AccessSession, user_id=user.id, token_hash=digest(token), expires_at=expiry)
    return SessionOut(user=UserOut.model_validate(user), access_token=token, expires_at=expiry)

@router.get('/me', response_model=UserOut)
def me(user=Depends(current_user)):
    return user

@router.delete('/sessions', status_code=204)
def logout(user=Depends(current_user), db=Depends(get_db)):
    db.execute(delete(AccessSession).where(AccessSession.user_id == user.id))
    return Response(status_code=204)

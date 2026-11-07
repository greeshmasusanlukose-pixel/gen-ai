import hashlib
import re
from datetime import datetime, timezone
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from app.database.session import get_db
from app.models.entities import AccessSession, User
from app.core.exceptions import AppError

bearer = HTTPBearer(auto_error=False)

def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_db)):
    if credentials is None:
        raise AppError(401, 'unauthorized', 'A bearer session is required')
    session = db.scalar(select(AccessSession).where(AccessSession.token_hash == digest(credentials.credentials)))
    if session is None or session.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        raise AppError(401, 'unauthorized', 'Session expired or invalid')
    return db.get(User, session.user_id)

def reject_secrets(text):
    # Conservative best-effort intake guard; cannot identify arbitrary unlabeled secrets.
    patterns = [r'\b\d{4,8}\b', r'(?i)(?:password|passwd|pin|otp|പാസ്‌വേഡ്|ഒടിപി)\s*(?:is|ആണ്|[:=])\s*\S+', r'(?i)(?:password|pin|otp)\s+[A-Za-z0-9]*\d[A-Za-z0-9]*']
    if any(re.search(p, text) for p in patterns):
        raise AppError(422, 'sensitive_input', 'Remove passwords, PINs and codes before sending / രഹസ്യ വിവരങ്ങൾ നീക്കം ചെയ്യുക')

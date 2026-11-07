from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from sqlalchemy import select
from app.core.security import current_user, reject_secrets
from app.database.session import get_db
from app.models.entities import Conversation, Message, UploadedFile
from app.repositories.records import add, owned
from app.schemas.api import ChatIn, ChatOut, HistoryOut, UploadOut, AIResult, SpeechIn, SpeechOut
from app.services.language import resolve_language
from app.services.file_service import process_upload
from app.services.ai_service import require_capability
from typing import Literal

router = APIRouter(prefix='/assistant', tags=['Assistant'])

@router.post('/chat', response_model=ChatOut)
async def chat(payload: ChatIn, request: Request, user=Depends(current_user), db=Depends(get_db)):
    reject_secrets(payload.text)
    conversation = owned(db, Conversation, payload.session_id, user.id) if payload.session_id else None
    history = []
    if conversation:
        messages = db.scalars(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at.desc()).limit(20)).all()
        history = [{'role': m.role, 'text': m.text} for m in reversed(messages)]
    language = resolve_language(payload.text, payload.language, user.language)
    require_capability(request.app.state.ai, 'chat')
    answer = await request.app.state.ai.chat(payload.text, language, history)
    reject_secrets(answer.text)
    for step in answer.steps:
        reject_secrets(step)
    if conversation is None:
        conversation = add(db, Conversation, user_id=user.id)
    add(db, Message, conversation_id=conversation.id, role='user', text=payload.text)
    add(db, Message, conversation_id=conversation.id, role='assistant', text=answer.text, is_mock=answer.is_mock)
    return ChatOut(session_id=conversation.id, answer=answer)

@router.get('/history/{session_id}', response_model=HistoryOut)
def history(session_id: str, user=Depends(current_user), db=Depends(get_db)):
    conversation = owned(db, Conversation, session_id, user.id)
    return HistoryOut(session_id=conversation.id, messages=conversation.messages)

@router.post('/upload', response_model=UploadOut, status_code=201)
async def upload(request: Request, file: UploadFile = File(...), language: Literal['ml', 'en'] = Form('ml'), user=Depends(current_user), db=Depends(get_db)):
    """Process a private file in memory; retain metadata only, never the original."""
    media, size, answer = await process_upload(file, language, request.app.state.settings, request.app.state.ai)
    item = add(db, UploadedFile, user_id=user.id, media_type=media, size=size, storage_name='not-retained')
    return UploadOut(file_id=item.id, media_type=media, size=size, answer=answer)

@router.post('/speech', response_model=SpeechOut)
async def speech(payload: SpeechIn, request: Request, user=Depends(current_user)):
    reject_secrets(payload.text)
    require_capability(request.app.state.ai, 'speak')
    return await request.app.state.ai.speak(payload.text, payload.language)

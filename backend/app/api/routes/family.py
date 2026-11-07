from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from app.database.session import get_db
from app.models.entities import User, FamilyMember, EmergencyContact, UserConsent, AssistanceRequest
from app.schemas.api import ContactIn, ContactOut, MemberIn, MemberOut, ConsentIn, ConsentOut, FamilyHelpIn, HelpOut
from app.core.security import current_user, reject_secrets
from app.core.exceptions import AppError
from app.repositories.records import owned, add, list_owned
from app.services.assistance_service import create_request

router = APIRouter(prefix='/family', tags=['Family'])

@router.post('/contacts', response_model=ContactOut, status_code=201)
def create_contact(payload: ContactIn, user=Depends(current_user), db=Depends(get_db)):
    reject_secrets(payload.name)
    return add(db, EmergencyContact, user_id=user.id, **payload.model_dump())

@router.get('/contacts', response_model=list[ContactOut])
def contacts(user=Depends(current_user), db=Depends(get_db)):
    return list_owned(db, EmergencyContact, user.id)

@router.delete('/contacts/{contact_id}', status_code=204)
def delete_contact(contact_id: str, user=Depends(current_user), db=Depends(get_db)):
    db.delete(owned(db, EmergencyContact, contact_id, user.id))
    return Response(status_code=204)

@router.post('/members', response_model=MemberOut, status_code=201)
def create_member(payload: MemberIn, user=Depends(current_user), db=Depends(get_db)):
    reject_secrets(payload.relationship_label)
    if payload.member_user_id == user.id or db.get(User, payload.member_user_id) is None:
        raise AppError(422, 'invalid_member', 'A different registered user is required')
    existing = db.scalar(select(FamilyMember).where(FamilyMember.user_id == user.id, FamilyMember.member_user_id == payload.member_user_id))
    if existing:
        raise AppError(409, 'duplicate_member', 'Family member already exists')
    return add(db, FamilyMember, user_id=user.id, **payload.model_dump())

@router.get('/members', response_model=list[MemberOut])
def members(user=Depends(current_user), db=Depends(get_db)):
    return list_owned(db, FamilyMember, user.id)

@router.put('/members/{member_id}/consent', response_model=ConsentOut)
def consent(member_id: str, payload: ConsentIn, user=Depends(current_user), db=Depends(get_db)):
    owned(db, FamilyMember, member_id, user.id)
    existing = db.scalar(select(UserConsent).where(UserConsent.family_member_id == member_id))
    if existing:
        existing.granted = payload.granted
        return existing
    return add(db, UserConsent, user_id=user.id, family_member_id=member_id, granted=payload.granted)

@router.post('/assistance', response_model=HelpOut, status_code=201)
def assistance(payload: FamilyHelpIn, user=Depends(current_user), db=Depends(get_db)):
    """Share only this request with the chosen family member, subject to active consent."""
    return create_request(db, user, payload, family=True)

@router.get('/assistance/inbox', response_model=list[HelpOut])
def inbox(user=Depends(current_user), db=Depends(get_db)):
    return db.scalars(select(AssistanceRequest).join(FamilyMember, AssistanceRequest.family_member_id == FamilyMember.id).join(UserConsent, UserConsent.family_member_id == FamilyMember.id).where(FamilyMember.member_user_id == user.id, UserConsent.granted.is_(True)).order_by(AssistanceRequest.created_at.desc()).limit(200)).all()

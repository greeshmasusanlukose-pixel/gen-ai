from fastapi import APIRouter, Depends
from sqlalchemy import select
from app.core.security import current_user
from app.database.session import get_db
from app.models.entities import AssistanceRequest, Helper
from app.schemas.api import HelpIn, HelpOut, HelpPatch, HelperOut
from app.repositories.records import owned, list_owned
from app.services.assistance_service import create_request, update_request

router = APIRouter(prefix='/human-help', tags=['Human help'])

@router.get('/helpers', response_model=list[HelperOut])
def helpers(user=Depends(current_user), db=Depends(get_db)):
    return db.scalars(select(Helper).where(Helper.verified.is_(True), Helper.available.is_(True)).limit(100)).all()

@router.post('/requests', response_model=HelpOut, status_code=201)
def create(payload: HelpIn, user=Depends(current_user), db=Depends(get_db)):
    return create_request(db, user, payload)

@router.get('/requests', response_model=list[HelpOut])
def requests(user=Depends(current_user), db=Depends(get_db)):
    return list_owned(db, AssistanceRequest, user.id)

@router.get('/requests/{request_id}', response_model=HelpOut)
def retrieve(request_id: str, user=Depends(current_user), db=Depends(get_db)):
    return owned(db, AssistanceRequest, request_id, user.id)

@router.patch('/requests/{request_id}', response_model=HelpOut)
def update(request_id: str, payload: HelpPatch, user=Depends(current_user), db=Depends(get_db)):
    """Owner-managed MVP workflow; helpers do not gain account access."""
    return update_request(db, owned(db, AssistanceRequest, request_id, user.id), payload)

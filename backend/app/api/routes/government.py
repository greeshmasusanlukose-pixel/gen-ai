from typing import Literal
from fastapi import APIRouter, Depends, Query
from app.database.session import get_db
from app.models.entities import GovernmentScheme
from app.schemas.api import SchemeList, SchemeOut
from app.services.government_service import search
from app.core.exceptions import AppError

router = APIRouter(prefix='/government', tags=['Government'])

@router.get('/schemes', response_model=SchemeList)
def schemes(q: str = Query('', max_length=200), language: Literal['ml', 'en'] | None = None, db=Depends(get_db)):
    items = search(db, q, language)
    return SchemeList(items=items, message='Reviewed catalogue results / പരിശോധിച്ച വിവരങ്ങൾ' if items else 'No verified information available / സ്ഥിരീകരിച്ച വിവരങ്ങൾ ലഭ്യമല്ല')

@router.get('/schemes/{scheme_id}', response_model=SchemeOut)
def scheme(scheme_id: str, db=Depends(get_db)):
    item = db.get(GovernmentScheme, scheme_id)
    if item is None or not item.verified:
        raise AppError(404, 'unverified_or_missing', 'Verified scheme information is unavailable')
    return item

from sqlalchemy import select
from app.models.entities import FamilyMember, UserConsent, AssistanceRequest, Helper
from app.repositories.records import owned, add
from app.core.exceptions import AppError
from app.core.security import reject_secrets

def check_consent(db, member):
    consent = db.scalar(select(UserConsent).where(UserConsent.family_member_id == member.id, UserConsent.granted.is_(True)))
    if consent is None:
        raise AppError(403, 'consent_required', 'Explicit assistance-sharing consent is required / അനുമതി ആവശ്യമാണ്')

def create_request(db, user, payload, family=False):
    reject_secrets(payload.description)
    values = payload.model_dump()
    if family:
        member = owned(db, FamilyMember, payload.family_member_id, user.id)
        check_consent(db, member)
    return add(db, AssistanceRequest, user_id=user.id, **values)

def update_request(db, item, payload):
    transitions = {'pending': {'assigned', 'cancelled'}, 'assigned': {'in_progress', 'cancelled'}, 'in_progress': {'resolved', 'cancelled'}, 'resolved': set(), 'cancelled': set()}
    if payload.status not in transitions[item.status]:
        raise AppError(409, 'invalid_transition', 'Invalid request status transition')
    if payload.status == 'assigned':
        if item.family_member_id:
            check_consent(db, db.get(FamilyMember, item.family_member_id))
            if payload.helper_id:
                raise AppError(422, 'invalid_helper', 'Family requests cannot be assigned to public helpers')
        else:
            helper = db.get(Helper, payload.helper_id) if payload.helper_id else None
            if helper is None or not helper.verified or not helper.available:
                raise AppError(422, 'invalid_helper', 'An available verified helper is required')
            item.helper_id = helper.id
    elif payload.helper_id:
        raise AppError(422, 'invalid_helper', 'Helper can only be set during assignment')
    if payload.status == 'resolved':
        if not payload.resolution:
            raise AppError(422, 'resolution_required', 'Resolution details are required')
        reject_secrets(payload.resolution)
        item.resolution = payload.resolution
    elif payload.resolution:
        raise AppError(422, 'invalid_resolution', 'Resolution is only accepted when resolving')
    item.status = payload.status
    db.flush()
    return item

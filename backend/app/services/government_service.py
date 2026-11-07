import json
from sqlalchemy import select
from app.models.entities import GovernmentScheme
from app.schemas.api import SchemeIn

def import_catalogue(db, path):
    if not path.exists():
        return
    for raw in json.loads(path.read_text(encoding='utf-8-sig')):
        item = SchemeIn.model_validate(raw)
        data = item.model_dump(mode='json')
        existing = db.get(GovernmentScheme, item.id)
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(GovernmentScheme(**data))

def search(db, query, language):
    statement = select(GovernmentScheme).where(GovernmentScheme.verified.is_(True))
    if query:
        statement = statement.where(GovernmentScheme.title.contains(query, autoescape=True) | GovernmentScheme.description.contains(query, autoescape=True))
    if language:
        statement = statement.where(GovernmentScheme.language == language)
    return db.scalars(statement.order_by(GovernmentScheme.title).limit(100)).all()

from sqlalchemy import select
from app.core.exceptions import AppError

def owned(db, model, record_id, user_id):
    item = db.get(model, record_id)
    if item is None or item.user_id != user_id:
        raise AppError(404, 'not_found', 'Record not found / രേഖ കണ്ടെത്തിയില്ല')
    return item

def add(db, model, **values):
    item = model(**values)
    db.add(item)
    db.flush()
    return item

def list_owned(db, model, user_id):
    return db.scalars(select(model).where(model.user_id == user_id).order_by(model.created_at).limit(200)).all()

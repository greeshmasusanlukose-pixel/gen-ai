from fastapi import Request
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.database.base import Base

def database(url):
    engine = create_engine(url, connect_args={'check_same_thread': False} if url.startswith('sqlite') else {})
    if url.startswith('sqlite'):
        @event.listens_for(engine, 'connect')
        def foreign_keys(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')
    return engine, sessionmaker(engine, expire_on_commit=False)

def get_db(request: Request):
    with request.app.state.sessions() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

from app.database.base import Database
from app.database.errors import DatabaseInitError

__db: Database

def init_db(db: Database):
    global __db
    __db = db

def get_db():
    if not __db:
        raise DatabaseInitError("Database is'nt initiated yet")
    return __db



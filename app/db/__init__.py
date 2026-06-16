from app.config import REDIS, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from app.db.db_context import DbContext
from app.db.redis import RedisManager
from . import models
from sqlalchemy.exc import SQLAlchemyError
from app.db.base import Base, SessionLocal


from .db_base import DBBase


tls_db: DBBase = DbContext(models.TLS)
node_db: DBBase = DbContext(models.Node)
excepted_ips: DBBase = DbContext(models.ExceptedIP)


class GetDB:  # Context Manager
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, _, exc_value, traceback):
        if isinstance(exc_value, SQLAlchemyError):
            self.db.rollback()  # rollback on exception

        self.db.close()

redis=REDIS and RedisManager(REDIS_HOST, REDIS_PORT, 0, REDIS_PASSWORD)
        
class GetRedisDB:  # Context Manager
    def __init__(self):
        self.db = redis

    def __enter__(self):
        return self.db

    def __exit__(self, _, exc_value, traceback):
        ""
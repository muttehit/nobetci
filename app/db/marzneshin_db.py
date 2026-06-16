import logging
from app.config import REDIS
from app.db import redis
from app.db.db_base import DBBase
from app.models.panel import Panel
from app.models.user import UserLimit
from app.utils.panel.marzneshin_panel import get_user_ip_limit

logger = logging.getLogger(__name__)


class MarzneshinDB(DBBase):
    def __init__(self, panel: Panel):
        self.panel = panel

    def save(self) -> None:
        ""

    def add(self, data):
        ''

    def delete(self, condition: callable):
        ''

    def update(self, condition: callable, data):
        ''

    async def get(self, condition: callable):
        username = getattr(condition.right, "value", condition.right)
        
        if REDIS and redis.exists(f'user:{username}:ip_limit'):
            return UserLimit(name=username, limit=int(redis.get(f'user:{username}:ip_limit') or 0))

        user_ip_limit = await get_user_ip_limit(self.panel, username)
        logger.debug(UserLimit(
            name=username, limit=user_ip_limit))
        return UserLimit(name=username, limit=user_ip_limit)

    def get_all(self, condition: callable):
        ''

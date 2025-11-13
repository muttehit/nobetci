import logging
from app.config import CACHE_TTL
from app.db.db_base import DBBase
from app.models.panel import Panel
from app.models.user import UserLimit
from app.utils.panel.rebecca_panel import get_user
from cachetools import TTLCache

logger = logging.getLogger(__name__)


class RebeccaDB(DBBase):
    def __init__(self, panel: Panel):
        self.panel = panel
        self.cache = TTLCache(maxsize=100000, ttl=CACHE_TTL)

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

        if username in self.cache:
            return UserLimit(name=self.cache[username].name, limit=self.cache[username].limit)

        self.cache[username] = UserLimit(name=username, limit=0)
        user = await get_user(username, self.panel)
        self.cache[username] = UserLimit(
            name=user["username"], limit=user['ip_limit'])
        logger.info(UserLimit(name=user["username"], limit=user['ip_limit']))
        return UserLimit(name=user["username"], limit=user['ip_limit'])

    def get_all(self, condition: callable):
        ''

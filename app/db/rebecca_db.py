import asyncio
import logging
from typing import Type
from app.config import PANEL_ADDRESS, PANEL_PASSWORD, PANEL_USERNAME
from app.db.base import SessionLocal
from app.db.db_base import DBBase
from app.models.panel import Panel
from app.models.user import UserLimit
from app.utils.panel.rebecca_panel import get_user

logger = logging.getLogger(__name__)


class RebeccaDB(DBBase):
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
        user = await get_user(getattr(condition.right, "value", condition.right), self.panel)
        return UserLimit(name=user["username"], limit=user['ip_limit'])

    def get_all(self, condition: callable):
        ''

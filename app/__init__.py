import logging

import uvicorn
from app.config import DEBUG
from app.db.db_context import DbContext
from app.db.models import UserLimit
from app.storage.memory import MemoryStorage


__version__ = "0.0.1"

storage = MemoryStorage()
user_limit_db = DbContext(UserLimit)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
handler = logging.StreamHandler()
formatter = uvicorn.logging.ColourizedFormatter(
    "{levelprefix:<8} @{name}: {message}", style="{", use_colors=True
)
handler.setFormatter(formatter)
logger.addHandler(handler)
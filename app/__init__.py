from app.db.db_context import DbContext
from app.db.models import UserLimit
from app.storage.memory import MemoryStorage


__version__ = "0.0.1"

storage = MemoryStorage()
user_limit_db = DbContext(UserLimit)
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from app.config import TELEGRAM_ADMIN_ID
from app.notification.telegram import send_notification


def restricted(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        print(update.effective_chat.id)
        if update.effective_chat.id not in TELEGRAM_ADMIN_ID:
            return await send_notification("⛔️ Access denied.")
        return await func(update, context, *args, **kwargs)
    return wrapper

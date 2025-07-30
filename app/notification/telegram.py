import logging
from telegram import Bot
from telegram.error import TelegramError
from app.config import (
    TELEGRAM_API_TOKEN,
    TELEGRAM_ADMIN_ID,
    TELEGRAM_LOGGER_CHANNEL_ID,
)

logger = logging.getLogger(__name__)


async def send_message(
    message: str,
    parse_mode='HTML',
):
    if not TELEGRAM_API_TOKEN or not (bot := Bot(token=TELEGRAM_API_TOKEN)):
        return

    for recipient_id in (TELEGRAM_ADMIN_ID or []) + [
        TELEGRAM_LOGGER_CHANNEL_ID
    ]:
        if not recipient_id:
            continue
        try:
            await bot.send_message(
                recipient_id,
                message,
                parse_mode=parse_mode,
            )
        except TelegramError as e:
            logger.error(e)


async def send_notification(notif: str):
    await send_message(notif)

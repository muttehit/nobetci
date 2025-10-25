import logging
from telegram import Bot, InlineKeyboardMarkup
from telegram.error import TelegramError
from app.config import (
    TELEGRAM_API_TOKEN,
    TELEGRAM_ADMIN_ID,
    TELEGRAM_LOGGER_CHANNEL_ID,
    TELEGRAM_LOGS,
)
from app.notification import get_ad

logger = logging.getLogger(__name__)


async def send_message(
    message: str,
    parse_mode='HTML',
    reply_markup=None
):
    if not TELEGRAM_LOGS or not TELEGRAM_API_TOKEN or not (bot := Bot(token=TELEGRAM_API_TOKEN)):
        return

    message += '\n➖➖➖➖➖➖➖➖\n' + get_ad()

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
                reply_markup=reply_markup
            )
        except TelegramError as e:
            logger.error(e)


async def send_notification(notif: str):
    await send_message(notif)


async def send_notification_with_reply_markup(notif: str, reply_markup: InlineKeyboardMarkup):
    await send_message(notif, reply_markup=reply_markup)

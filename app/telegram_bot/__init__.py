
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from app.config import TELEGRAM_API_TOKEN


async def build_telegram_bot():
    if not TELEGRAM_API_TOKEN or not (application := ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()):
        return

    application.add_handler(CommandHandler("start", start))

    while True:
        try:
            async with application:
                await application.start()
                await application.updater.start_polling()
                while True:
                    await asyncio.sleep(40)
        except Exception:
            continue


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(text=START_MESSAGE)


START_MESSAGE = """
<b>Commands List:</b>\n
<b>/start</b>
"""

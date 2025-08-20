
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
from app import user_limit_db

(
    GET_USER_NAME,
    GET_USER_LIMIT
) = range(2)


async def build_telegram_bot():
    if not TELEGRAM_API_TOKEN or not (application := ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()):
        return

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("add_user", add_user)],
            states={
                GET_USER_NAME: [MessageHandler(filters.TEXT, get_user_name)],
                GET_USER_LIMIT: [MessageHandler(filters.TEXT, get_user_limit)]
            },
            fallbacks=[],
        )
    )

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


async def add_user(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="Send Your User Name:"
    )
    return GET_USER_NAME


async def get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your User Limit: (For example: 1)",
    )
    return GET_USER_LIMIT


async def get_user_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["limit"] = update.message.text.strip()

    user_limit_db.add({"name": context.user_data["name"], "limit": context.user_data["limit"]})

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"User {context.user_data["name"]} added with limit {context.user_data["limit"]}"
    )
    return ConversationHandler.END

START_MESSAGE = """
<b>Commands List:</b>\n
<b>/start</b>
"""


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
from app.db.models import UserLimit

(
    ADD_USER_NAME,
    ADD_USER_LIMIT,
    GET_USER_NAME,
    UPDATE_USER_NAME,
    UPDATE_USER_LIMIT,
    DELETE_USER_NAME
) = range(6)


async def build_telegram_bot():
    if not TELEGRAM_API_TOKEN or not (application := ApplicationBuilder().token(TELEGRAM_API_TOKEN).build()):
        return

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("add_user", add_user)],
            states={
                ADD_USER_NAME: [MessageHandler(filters.TEXT, add_user_name)],
                ADD_USER_LIMIT: [MessageHandler(filters.TEXT, add_user_limit)]
            },
            fallbacks=[CommandHandler("cancel", start)],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("get_user", get_user)],
            states={
                GET_USER_NAME: [MessageHandler(filters.TEXT, get_user_name)]
            },
            fallbacks=[CommandHandler("cancel", start)],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("update_user", update_user)],
            states={
                UPDATE_USER_NAME: [MessageHandler(filters.TEXT, update_user_name)],
                UPDATE_USER_LIMIT: [MessageHandler(
                    filters.TEXT, update_user_limit)]
            },
            fallbacks=[CommandHandler("cancel", start)],
        )
    )
    application.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("delete_user", delete_user)],
            states={
                DELETE_USER_NAME: [MessageHandler(
                    filters.TEXT, delete_user_name)]
            },
            fallbacks=[CommandHandler("cancel", start)],
        )
    )

    application.add_handler(MessageHandler(filters.TEXT, start))
    application.add_handler(MessageHandler(filters.COMMAND, start))

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


async def get_user(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="Send Your User Name:"
    )
    return GET_USER_NAME


async def get_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()

    user = user_limit_db.get(UserLimit.name == context.user_data["name"])

    if not user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="User Isn't Exists"
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"User {user.name} limit is {user.limit}",
    )
    return ConversationHandler.END


async def add_user(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="Send Your User Name:"
    )
    return ADD_USER_NAME


async def add_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()

    if user_limit_db.get(UserLimit.name == context.user_data["name"]):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="User Is Exists"
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your User Limit: (For example: 1)",
    )
    return ADD_USER_LIMIT


async def add_user_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["limit"] = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/update_user</b>"
        )
        return ConversationHandler.END

    user_limit_db.add(
        {"name": context.user_data["name"], "limit": context.user_data["limit"]})

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"User {context.user_data["name"]} added with limit {context.user_data["limit"]}"
    )
    return ConversationHandler.END


async def update_user(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="Send Your User Name:"
    )
    return UPDATE_USER_NAME


async def update_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()

    if not user_limit_db.get(UserLimit.name == context.user_data["name"]):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="User Isn't Exists"
        )
        return ConversationHandler.END

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Send Your User Limit: (For example: 1)",
    )
    return UPDATE_USER_LIMIT


async def update_user_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["limit"] = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_html(
            text=f"Wrong input: <code>{update.message.text.strip()}"
            + "</code>\ntry again <b>/update_user</b>"
        )
        return ConversationHandler.END

    user_limit_db.update(UserLimit.name == context.user_data["name"], {
        "limit": context.user_data["limit"]})

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"User {context.user_data["name"]} updated with limit {context.user_data["limit"]}"
    )
    return ConversationHandler.END


async def delete_user(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text="Send Your User Name:"
    )
    return DELETE_USER_NAME


async def delete_user_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text.strip()

    if not user_limit_db.get(UserLimit.name == context.user_data["name"]):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="User Isn't Exists"
        )
        return ConversationHandler.END

    user_limit_db.delete(UserLimit.name == context.user_data["name"])

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"User {context.user_data["name"]} deleted",
    )
    return ConversationHandler.END

START_MESSAGE = """
<b>Commands List:</b>
<b>/start</b>
<code>start the bot</code>
<b>/get_user</b>
<code>Get User Limit</code>
<b>/add_user</b>
<code>Add User</code>
<b>/update_user</b>
<code>Update User</code>
<b>/delete_user</b>
<code>Delete User</code>
"""

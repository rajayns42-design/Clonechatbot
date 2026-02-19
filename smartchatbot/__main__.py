import logging
import asyncio
import sys

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)

# =========================
# IMPORTS
# =========================

from .config import TOKEN, LOGGER_GROUP
from .database import get_all_bots, add_user

from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import (
    welcome_toggle,
    welcome_member,
    master_start,
    help_callback
)

from .modules.cloner import (
    clone_bot,
    delclone_bot,
    anti_nsfw_delete,
    broadcast_handler
)

from .modules.admin import (
    ban_user,
    unban_user,
    mute_user,
    unmute_user,
    promote_user,
    get_admin_list
)

from .modules.ping import ping_handler, ping_callback_handler


logging.basicConfig(level=logging.INFO)


# =========================
# LOGGER
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.effective_user:
        return

    user = update.effective_user
    add_user(user.id)

    # log only /start
    if update.message and update.message.text and update.message.text.startswith("/start"):

        text = (
            "👤 <b>NEW START</b>\n\n"
            f"🤖 Bot: @{context.bot.username}\n"
            f"🆔 <code>{user.id}</code>\n"
            f"📝 {user.first_name}"
        )

        try:
            await context.bot.send_message(
                LOGGER_GROUP,
                text,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(e)


# =========================
# HANDLERS
# =========================

def register_all_handlers(app: Application):

    # -------- COMMANDS --------
    app.add_handler(CommandHandler("start", master_start), group=0)
    app.add_handler(CommandHandler("help", help_callback), group=0)
    app.add_handler(CommandHandler("ping", ping_handler), group=0)

    app.add_handler(CommandHandler("clone", clone_bot), group=0)
    app.add_handler(CommandHandler("delclone", delclone_bot), group=0)
    app.add_handler(CommandHandler("broadcast", broadcast_handler), group=0)

    app.add_handler(CommandHandler("chatbot", chatbot_toggle), group=0)
    app.add_handler(CommandHandler("welcome", welcome_toggle), group=0)

    app.add_handler(CommandHandler("ban", ban_user), group=0)
    app.add_handler(CommandHandler("unban", unban_user), group=0)
    app.add_handler(CommandHandler("mute", mute_user), group=0)
    app.add_handler(CommandHandler("unmute", unmute_user), group=0)
    app.add_handler(CommandHandler("promote", promote_user), group=0)
    app.add_handler(CommandHandler("adminlist", get_admin_list), group=0)

    # -------- CALLBACKS --------
    app.add_handler(CallbackQueryHandler(master_start, pattern="^start"), group=1)
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help"), group=1)
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping"), group=1)

    # -------- LOGGER --------
    app.add_handler(MessageHandler(filters.ALL, log_user_start), group=2)

    # -------- NSFW --------
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL,
            anti_nsfw_delete
        ),
        group=3
    )

    # -------- WELCOME --------
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member),
        group=4
    )

    # -------- CHATBOT LAST --------
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply),
        group=5
    )


# =========================
# UI COMMANDS
# =========================

async def set_ui_commands(bot):
    await bot.set_my_commands([
        BotCommand("start", "Start bot"),
        BotCommand("help", "Help menu"),
        BotCommand("ping", "Check speed"),
        BotCommand("clone", "Clone bot"),
        BotCommand("delclone", "Delete clone"),
        BotCommand("broadcast", "Broadcast"),
        BotCommand("chatbot", "Toggle AI"),
        BotCommand("welcome", "Welcome toggle"),
        BotCommand("adminlist", "Admins list"),
    ])


# =========================
# RESTART CLONES
# =========================

async def restart_clones():

    bots = get_all_bots()

    for bot in bots:
        try:
            clone_app = Application.builder().token(bot["token"]).build()
            register_all_handlers(clone_app)
            await clone_app.initialize()
            await clone_app.start()
            print("Clone restarted:", bot.get("username"))
        except Exception as e:
            logging.error(e)


# =========================
# POST INIT
# =========================

async def post_init(app: Application):

    await set_ui_commands(app.bot)
    await restart_clones()

    # ✅ BOT ONLINE LOGGER
    try:
        await app.bot.send_message(
            LOGGER_GROUP,
            f"🟢 <b>BOT ONLINE</b>\n\n🤖 @{app.bot.username} running",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(e)


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        sys.exit("TOKEN missing")

    app = Application.builder().token(TOKEN).post_init(post_init).build()

    register_all_handlers(app)

    print("⚡ BOT RUNNING ⚡")

    app.run_polling()


if __name__ == "__main__":
    main()

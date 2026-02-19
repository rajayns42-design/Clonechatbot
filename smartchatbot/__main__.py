import logging
import sys

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# IMPORTS
# =========================

from .config import TOKEN, LOGGER_GROUP
from .database import get_all_bots, add_user

from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member, master_start, help_callback
from .modules.cloner import clone_bot, delclone_bot, anti_nsfw_delete, broadcast_handler
from .modules.admin import (
    ban_user, unban_user, mute_user, unmute_user,
    promote_user, get_admin_list
)
from .modules.ping import ping_handler, ping_callback_handler


logging.basicConfig(level=logging.INFO)

# =========================
# SAFE LOGGER
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.effective_user:
            return

        user = update.effective_user
        add_user(user.id)

        if update.message and update.message.text and update.message.text.startswith("/start"):
            text = (
                "👤 <b>NEW START</b>\n\n"
                f"🤖 @{context.bot.username}\n"
                f"🆔 <code>{user.id}</code>\n"
                f"📝 {user.first_name}"
            )

            await context.bot.send_message(
                LOGGER_GROUP,
                text,
                parse_mode="HTML"
            )

    except Exception as e:
        logging.error(f"LOGGER ERROR: {e}")


# =========================
# HANDLER REGISTER
# =========================

def register_all_handlers(app: Application):

    # -------- COMMANDS --------
    app.add_handler(CommandHandler("start", master_start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CommandHandler("ping", ping_handler))

    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # -------- CALLBACKS --------
    app.add_handler(CallbackQueryHandler(master_start, pattern="^start"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help"))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping"))

    # -------- LOGGER (non blocking) --------
    app.add_handler(
        MessageHandler(filters.ALL, log_user_start),
        block=False
    )

    # -------- NSFW --------
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL,
            anti_nsfw_delete
        )
    )

    # -------- WELCOME --------
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member)
    )

    # -------- CHATBOT SAFE WRAPPER --------
    async def safe_chatbot(update, context):
        try:
            await chatbot_reply(update, context)
        except Exception as e:
            logging.error(f"CHATBOT ERROR: {e}")

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, safe_chatbot)
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
# CLONE RESTART
# =========================

async def restart_clones():
    bots = get_all_bots()

    for bot in bots:
        try:
            clone_app = Application.builder().token(bot["token"]).build()
            register_all_handlers(clone_app)
            await clone_app.initialize()
            await clone_app.start()
            print("✅ Clone restarted:", bot.get("username"))
        except Exception as e:
            logging.error(f"CLONE ERROR: {e}")


# =========================
# POST INIT
# =========================

async def post_init(app: Application):

    await set_ui_commands(app.bot)
    await restart_clones()

    try:
        await app.bot.send_message(
            LOGGER_GROUP,
            f"🟢 <b>BOT ONLINE</b>\n\n🤖 @{app.bot.username}",
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(e)


# =========================
# MAIN
# =========================

def main():

    if not TOKEN:
        sys.exit("❌ TOKEN missing")

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    register_all_handlers(app)

    print("⚡ BOT RUNNING ⚡")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

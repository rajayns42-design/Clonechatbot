import logging
import asyncio
import sys

# Spelling Fix: 'import' (small i)
import logging
import asyncio

from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from .config import TOKEN, OWNER_ID
from .database import get_all_bots, add_user, get_all_users
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.cloner import (
    clone_bot,
    clone_start_handler,
    anti_nsfw_delete,
    broadcast_handler,
    delclone_bot
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

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# UI COMMAND MENU
# =========================
async def set_ui_commands(bot):
    commands = [
        BotCommand("start", "Start bot"),
        BotCommand("ping", "Check speed"),
        BotCommand("clone", "Create clone"),
        BotCommand("delclone", "Delete clone"),
        BotCommand("chatbot", "Toggle chatbot"),
        BotCommand("welcome", "Toggle welcome"),
        BotCommand("adminlist", "Admins list"),
        BotCommand("broadcast", "Owner only broadcast"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logging.error(f"Error setting commands: {e}")

# =========================
# AUTO SAVE USERS
# =========================
async def auto_store_user(update, context):
    if update.effective_user:
        add_user(update.effective_user.id)

# =========================
# REGISTER ALL HANDLERS
# =========================
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="close_ping"))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL) & ~filters.COMMAND,
        anti_nsfw_delete
    ), group=1)
    app.add_handler(MessageHandler(filters.ALL, auto_store_user), group=0)

# =========================
# RESTART CLONES FROM DB (FIXED)
# =========================
async def restart_clones(main_app: Application):
    bots = get_all_bots()
    if not bots:
        logging.info("No clones to restart")
        return

    for bot in bots:
        try:
            # FIXED: job_queue hata diya taaki NoneType error na aaye
            clone_app = Application.builder().token(bot["token"]).build()
            await set_ui_commands(clone_app.bot)
            register_all_handlers(clone_app)
            await clone_app.initialize()
            await clone_app.start()
            logging.info(f"✅ Clone started @{bot.get('username')}")
        except Exception as e:
            logging.error(f"❌ Clone failed for {bot.get('username')}: {e}")

# =========================
# MAIN BOT ENTRY (FIXED)
# =========================
def main():
    if not TOKEN:
        logging.error("TOKEN missing in config")
        return

    # Builder bina kisi extra parameter ke
    app = Application.builder().token(TOKEN).build()
    register_all_handlers(app)

    # Startup logic bina job_queue ke (Heroku safe)
    async def post_init(application: Application):
        await set_ui_commands(application.bot)
        await restart_clones(application)

    # loop me task schedule karna
    loop = asyncio.get_event_loop()
    loop.create_task(post_init(app))

    print(f"⚡ MAIN BOT RUNNING ⚡ | OWNER: {OWNER_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()

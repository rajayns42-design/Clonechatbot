import logging
import asyncio
import sys

# Standard Telegram Imports
from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

# Custom Imports
from .config import TOKEN, OWNER_ID
from .database import get_all_bots, add_user, get_all_users
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import (
    welcome_toggle, 
    welcome_member, 
    master_start, 
    help_callback
)
from .modules.cloner import (
    clone_bot,
    delclone_bot,     # <--- Yeh raha Delclone
    anti_nsfw_delete,
    broadcast_handler
)
from .modules.admin import (
    ban_user,
    unban_user,       # <--- Yeh raha Unban
    mute_user,
    unmute_user,      # <--- Yeh raha Unmute
    promote_user,
    get_admin_list
)
from .modules.ping import ping_handler, ping_callback_handler

# =========================
# LOGGING SETUP
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
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help menu"),
        BotCommand("ping", "Check speed ⚡"),
        BotCommand("clone", "Create bot clone 🚀"),
        BotCommand("delclone", "Delete your clone 🗑"), # <--- Menu mein add kiya
        BotCommand("promote", "Promote user"),
        BotCommand("ban", "Ban user"),
        BotCommand("unban", "Unban user"),
        BotCommand("mute", "Mute user"),
        BotCommand("unmute", "Unmute user"),
        BotCommand("chatbot", "Toggle AI"),
        BotCommand("welcome", "Toggle Welcome"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logging.error(f"Error: {e}")

# =========================
# AUTO USER SAVE
# =========================
async def auto_store_user(update, context):
    if update.effective_user:
        add_user(update.effective_user.id)

# =========================
# REGISTER ALL HANDLERS (FULL & FINAL)
# =========================
def register_all_handlers(app: Application):
    # 1. START & HELP
    app.add_handler(CommandHandler("start", master_start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CallbackQueryHandler(master_start, pattern="start_back"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="help_back"))

    # 2. PING & CALLBACK
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="close_ping"))

    # 3. CLONE SYSTEM (DELCLONE INCLUDED)
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot)) # <--- Registration Fixed!

    # 4. ADMIN SYSTEM (Full Suite)
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # 5. BROADCAST & OWNER TOOLS
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    # 6. FEATURES (AI & WELCOME)
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    # 7. MESSAGES & STATUS HANDLERS
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # 8. ANTI-NSFW & GROUP SAFETY
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL) & ~filters.COMMAND,
        anti_nsfw_delete
    ), group=1)
    
    # 9. AUTO SAVE
    app.add_handler(MessageHandler(filters.ALL, auto_store_user), group=0)

# =========================
# RESTART CLONES FROM DATABASE
# =========================
async def restart_clones(main_app: Application):
    bots = get_all_bots()
    if not bots:
        return
    for bot in bots:
        try:
            clone_app = Application.builder().token(bot["token"]).build()
            await set_ui_commands(clone_app.bot)
            register_all_handlers(clone_app)
            await clone_app.initialize()
            await clone_app.start()
        except:
            pass

# =========================
# MAIN ENTRY
# =========================
def main():
    if not TOKEN:
        logging.error("TOKEN MISSING!")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()
    register_all_handlers(app)

    async def post_init(application: Application):
        await set_ui_commands(application.bot)
        await restart_clones(application)

    loop = asyncio.get_event_loop()
    loop.create_task(post_init(app))

    print("⚡ NATKHAT BOT IS FULLY LOADED WITH ALL COMMANDS! ⚡")
    app.run_polling()

if __name__ == "__main__":
    main()

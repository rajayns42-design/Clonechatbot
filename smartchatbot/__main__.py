import logging
import asyncio
import sys
import time

# Standard Telegram Imports
from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)

# Custom Imports
from .config import TOKEN, OWNER_ID, LOGGER_GROUP, CLONE_LOGGER
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

# =========================
# 🔄 LOGGER SYSTEM (MESSAGES BHEJNE KE LIYE)
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Naye user ka log group mein bhejta hai"""
    if not update.effective_user:
        return
    
    user = update.effective_user
    bot = context.bot
    
    # Database mein save karein
    add_user(user.id)
    
    # Sirf /start par logger message bhejne ke liye logic
    if update.message and update.message.text == "/start":
        text = (
            "👤 **NEW USER STARTED!**\n\n"
            f"🤖 **Bot:** @{bot.username}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"📝 **Name:** {user.first_name}\n"
            f"🏷 **Username:** @{user.username if user.username else 'N/A'}"
        )
        try:
            await context.bot.send_message(chat_id=LOGGER_GROUP, text=text, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Logger Error: {e}")

# =========================
# REGISTER ALL HANDLERS
# =========================
def register_all_handlers(app: Application):
    # 1. LOGGER & AUTO SAVE (Priority 0)
    app.add_handler(MessageHandler(filters.ALL, log_user_start), group=0)

    # 2. START & HELP
    app.add_handler(CommandHandler("start", master_start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CallbackQueryHandler(master_start, pattern="start_back"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="help_back"))

    # 3. PING
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="close_ping"))

    # 4. CLONE SYSTEM
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))

    # 5. ADMIN SYSTEM
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # 6. FEATURES
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    # 7. CHATBOT & WELCOME
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # 8. ANTI-NSFW
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL) & ~filters.COMMAND,
        anti_nsfw_delete
    ), group=1)

# =========================
# UI & RUN
# =========================
async def set_ui_commands(bot):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("ping", "Check speed ⚡"),
        BotCommand("clone", "Create bot clone 🚀"),
        BotCommand("delclone", "Delete clone 🗑"),
        BotCommand("chatbot", "Toggle AI"),
    ]
    await bot.set_my_commands(commands)

async def restart_clones(main_app: Application):
    bots = get_all_bots()
    for bot in bots:
        try:
            clone_app = Application.builder().token(bot["token"]).build()
            register_all_handlers(clone_app)
            await clone_app.initialize()
            await clone_app.start()
        except: pass

def main():
    if not TOKEN: sys.exit(1)
    app = Application.builder().token(TOKEN).build()
    register_all_handlers(app)

    async def post_init(application: Application):
        await set_ui_commands(application.bot)
        await restart_clones(application)

    loop = asyncio.get_event_loop()
    loop.create_task(post_init(app))
    
    print("⚡ BOT STARTED & LOGGER ACTIVE ⚡")
    app.run_polling()

if __name__ == "__main__":
    main()

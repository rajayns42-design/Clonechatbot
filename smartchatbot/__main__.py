import logging
import sys
import asyncio
import time

from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# =========================
# CONFIG & DB IMPORT
# =========================
from .config import TOKEN, LOGGER_GROUP, OWNER_ID, START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL, OWNER_USERNAME
from .database import add_user, get_all_users, get_welcome_status

# =========================
# MODULES (FIXED IMPORTS)
# =========================
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.start import start, help_callback  # <-- start.py se sahi functions load kiye
from .modules.admin import ban_user, unban_user, mute_user, unmute_user, promote_user, get_admin_list
from .modules.ping import ping_handler, ping_callback_handler

logging.basicConfig(level=logging.INFO)

# =========================
# OWNER ONLY BROADCAST
# =========================
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != int(OWNER_ID):
        await update.message.reply_text("❌ Ye command sirf Bot Owner use kar sakta hai!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Reply to any message to broadcast it to all users.")
        return

    msg = update.message.reply_to_message
    users = get_all_users()
    sent = 0
    failed = 0
    status_msg = await update.message.reply_text(f"🚀 Broadcasting to {len(users)} users...")

    for uid in users:
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=msg.chat_id, message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1

    await status_msg.edit_text(f"✅ Broadcast finished!\n👤 Success: `{sent}`\n❌ Failed: `{failed}`", parse_mode="Markdown")

# =========================
# LOG USER START
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        add_user(update.effective_user.id)

# =========================
# SAFE CHATBOT CALL
# =========================
async def safe_chatbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await chatbot_reply(update, context)
    except Exception as e:
        logging.error(f"CHATBOT ERROR: {e}")

# =========================
# REGISTER HANDLERS (FIXED)
# =========================
def register_all_handlers(app: Application):
    # Commands
    app.add_handler(CommandHandler("start", start)) # <-- master_start ko badal kar start kiya
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    # Admin commands
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # Callbacks (Fixed master_start issue)
    app.add_handler(CallbackQueryHandler(start, pattern="^start"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help"))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping"))

    # New members welcome
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # Save user ID
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, log_user_start))

    # AI Chatbot
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, safe_chatbot))

# =========================
# POST INIT BOT COMMANDS
# =========================
async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Start bot"),
        BotCommand("help", "Help menu"),
        BotCommand("ping", "Check speed"),
        BotCommand("broadcast", "Owner Only Broadcast"),
        BotCommand("chatbot", "Toggle AI"),
        BotCommand("adminlist", "Admins list"),
        BotCommand("welcome", "Enable/Disable Welcome"),
    ])
    try:
        await app.bot.send_message(LOGGER_GROUP, "🟢 Bot is Online (All Features Active)")
    except: 
        pass

# =========================
# MAIN
# =========================
def main():
    if not TOKEN:
        sys.exit("❌ TOKEN missing")

    app = Application.builder().token(TOKEN).post_init(post_init).build()
    register_all_handlers(app)
    print("⚡ BOT RUNNING ⚡")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

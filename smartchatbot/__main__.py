import logging
import sys
import asyncio
import time

from telegram import BotCommand, Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from .config import TOKEN, LOGGER_GROUP, OWNER_ID
from .database import add_user, get_all_users

# =========================
# MODULES IMPORT
# =========================
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.start import start, help_callback, ping_handler, ping_callback_handler, close_msg
from .modules.admin import ban_user, unban_user, mute_user, unmute_user, promote_user, get_admin_list

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# NEW USER LOGGER & DB SAVE
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return
    
    user = update.effective_user
    # Database mein user add karna
    add_user(user.id)
    
    # Logger Group mein message bhejna (Sirf /start par)
    if update.message and update.message.text and update.message.text.startswith("/start"):
        log_text = (
            f"<b>🔔 #NewUser_Started</b>\n\n"
            f"👤 <b>Name:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}\n"
            f"🌍 <b>Link:</b> <a href='tg://user?id={user.id}'>User Link</a>"
        )
        try:
            await context.bot.send_message(
                chat_id=LOGGER_GROUP,
                text=log_text,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Logger Error: {e}")

# =========================
# OWNER ONLY BROADCAST
# =========================
async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != int(OWNER_ID):
        await update.message.reply_text("❌ Owner Only Command!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Message ko reply karke /broadcast likho.")
        return

    msg = update.message.reply_to_message
    users = get_all_users()
    sent = 0
    status_msg = await update.message.reply_text(f"🚀 Broadcasting to {len(users)} users...")

    for uid in users:
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=msg.chat_id, message_id=msg.message_id)
            sent += 1
            await asyncio.sleep(0.05)
        except:
            continue

    await status_msg.edit_text(f"✅ Broadcast Done! Sent to `{sent}` users.")

# =========================
# REGISTER ALL HANDLERS
# =========================
def register_all_handlers(app: Application):
    # User Logging (Sabse pehle check hoga)
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r"^/start"), log_user_start), group=-1)

    # Main Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    # Admin Module
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # Callbacks (Button clicks)
    app.add_handler(CallbackQueryHandler(start, pattern="^start_back$"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_menu$"))
    app.add_handler(CallbackQueryHandler(ping_handler, pattern="^ping_btn$"))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping$"))
    app.add_handler(CallbackQueryHandler(close_msg, pattern="^close_msg$"))

    # Welcome System
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # AI Chatbot (Text messages par reply)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

# =========================
# RUN BOT
# =========================
async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Start Bot"),
        BotCommand("help", "Command List"),
        BotCommand("ping", "Check Speed"),
        BotCommand("chatbot", "Toggle AI"),
    ])
    try:
        await app.bot.send_message(LOGGER_GROUP, "<b>🟢 Bot is Online</b>", parse_mode="HTML")
    except: pass

def main():
    if not TOKEN:
        sys.exit("❌ TOKEN MISSING!")

    app = Application.builder().token(TOKEN).post_init(post_init).build()
    register_all_handlers(app)
    
    print("⚡ BOT STARTED SUCCESSFULLY ⚡")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

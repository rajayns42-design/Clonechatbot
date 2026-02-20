import logging
import sys
import asyncio
from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Config & DB
from .config import TOKEN, LOGGER_GROUP, OWNER_ID
from .database import add_user, get_all_users

# Modules (Make sure these exist in start.py)
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.start import start, help_callback, ping_handler, ping_callback_handler, close_msg

logging.basicConfig(level=logging.INFO)

# =========================
# NEW USER LOGGER (NOTIFY)
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return
    
    user = update.effective_user
    # 1. Database mein add karna
    add_user(user.id)
    
    # 2. Logger group notification (Sirf /start par)
    if update.message.text and update.message.text.startswith("/start"):
        log_text = (
            f"<b>🔔 #NewUser_Started</b>\n\n"
            f"👤 <b>Name:</b> {user.first_name}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
            f"🔗 <b>Username:</b> @{user.username if user.username else 'None'}"
        )
        try:
            await context.bot.send_message(chat_id=LOGGER_GROUP, text=log_text, parse_mode="HTML")
        except: pass

# =========================
# REGISTER ALL HANDLERS
# =========================
def register_all_handlers(app: Application):
    # Logger first (Group -1)
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r"^/start"), log_user_start), group=-1)

    # Main Commands (Ye commands ab reply dengi)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))

    # Callback Query (Buttons ke liye)
    app.add_handler(CallbackQueryHandler(start, pattern="^start_back$"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_menu$"))
    app.add_handler(CallbackQueryHandler(ping_handler, pattern="^ping_btn$"))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping$"))
    app.add_handler(CallbackQueryHandler(close_msg, pattern="^close_msg$"))

    # Chatbot Reply (Always at the end)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

async def post_init(app: Application):
    # Menu button mein commands dikhane ke liye
    await app.bot.set_my_commands([
        BotCommand("start", "Natkhat ko shuru karein"),
        BotCommand("ping", "Bot speed check"),
        BotCommand("help", "Command list"),
    ])
    try: await app.bot.send_message(LOGGER_GROUP, "🟢 <b>Natkhat is now Online!</b>", parse_mode="HTML")
    except: pass

def main():
    if not TOKEN: sys.exit("❌ TOKEN MISSING")
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    register_all_handlers(app)
    print("⚡ NATKHAT BOT IS LIVE ⚡")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

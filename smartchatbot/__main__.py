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

# Modules (Imports ensure functions exist in start.py)
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.start import start, help_callback, ping_handler, ping_callback_handler, close_msg

logging.basicConfig(level=logging.INFO)

# =========================
# NEW USER LOGGER (NOTIFICATION)
# =========================
async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return
    
    user = update.effective_user
    # 1. Database mein add karna
    add_user(user.id)
    
    # 2. Logger group mein notification bhej raha hai
    if update.message.text and update.message.text.startswith("/start"):
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
            logging.error(f"Logger Error: {e}")

# =========================
# REGISTER HANDLERS
# =========================
def register_all_handlers(app: Application):
    # Logging first (Group -1)
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r"^/start"), log_user_start), group=-1)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))

    # Callbacks (Patterns fixed)
    app.add_handler(CallbackQueryHandler(start, pattern="^start_back$"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help_menu$"))
    app.add_handler(CallbackQueryHandler(ping_handler, pattern="^ping_btn$"))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping$"))
    app.add_handler(CallbackQueryHandler(close_msg, pattern="^close_msg$"))

    # Chatbot Reply (Text and Reply triggers)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Start Bot"),
        BotCommand("ping", "Check Speed"),
        BotCommand("help", "Help Menu"),
    ])
    try:
        await app.bot.send_message(LOGGER_GROUP, "<b>🟢 Bot Online & Active!</b>", parse_mode="HTML")
    except: pass

def main():
    if not TOKEN: sys.exit("❌ TOKEN MISSING")
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    register_all_handlers(app)
    print("⚡ NATKHAT IS RUNNING ⚡")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

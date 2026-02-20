import logging
import sys
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ChatMemberHandler, 
    CallbackQueryHandler,
    ContextTypes
)

# ==========================================
# ✶ ABSOLUTE IMPORTS (Final Fix for Heroku)
# ==========================================
# Hum 'smartchatbot' package name use kar rahe hain taaki 
# Heroku ko file location mil sake.
from smartchatbot.config import Config
from smartchatbot.database import register_user
from smartchatbot.modules.start import start, help_menu, help_button_callback
from smartchatbot.modules.ping import ping
from smartchatbot.modules.chatbot import chatbot_reply, chatbot_toggle
from smartchatbot.modules.admin import (
    get_admin_list, ban_user, unban_user, 
    mute_user, unmute_user, promote_user, 
    get_user_id, welcome_toggle
)
from smartchatbot.modules.welcome import welcome_member
from smartchatbot.modules.logging import log_bot_on, log_group_add
from smartchatbot.modules.broadcast import broadcast_handler

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Bot ko chalu karein ✨"),
        BotCommand("ping", "Bot ki speed check karein ⚡"),
        BotCommand("help", "Saari commands ki list dekhein 📖"),
        BotCommand("id", "Apni ya group ki ID jaanein 🆔"),
        BotCommand("chatbot", "AI Chatbot ON/OFF karein 🤖"),
        BotCommand("welcome", "Welcome message ON/OFF karein 🤝"),
        BotCommand("admins", "Admins ki list dekhein 👮"),
        BotCommand("ban", "User ko ban karein 🚫"),
        BotCommand("unban", "User ko unban karein 🔓"),
        BotCommand("mute", "User ko mute karein 🤫"),
        BotCommand("unmute", "User ko unmute karein 🔊"),
        BotCommand("broadcast", "Msg sabhi ko bhejin (Owner) 📢"),
    ]
    await application.bot.set_my_commands(commands)

async def post_init(application):
    await set_bot_commands(application)
    try:
        await log_bot_on(application)
        print("🚀 NATKHAT SYSTEM: ONLINE")
    except Exception as e:
        print(f"Startup Log Error: {e}")

async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

def main():
    if not Config.BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN is missing!")
        return

    application = ApplicationBuilder().token(Config.BOT_TOKEN).post_init(post_init).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("id", get_user_id))
    
    application.add_handler(CallbackQueryHandler(help_button_callback, pattern="^(help_menu|back_start)$"))
    application.add_handler(CallbackQueryHandler(close_callback, pattern="close_msg"))

    application.add_handler(CommandHandler("admins", get_admin_list))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    application.add_handler(CommandHandler("promote", promote_user))
    application.add_handler(CommandHandler("chatbot", chatbot_toggle))
    application.add_handler(CommandHandler("welcome", welcome_toggle))
    application.add_handler(CommandHandler("broadcast", broadcast_handler))

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    application.add_handler(ChatMemberHandler(log_group_add, ChatMemberHandler.MY_CHAT_MEMBER))

    print("NATKHAT is Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

import logging
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

# Configuration & Database logic
from config import Config
from database import register_user

# Modules Import
from modules.start import start, help_menu, help_button_callback
from modules.ping import ping
from modules.chatbot import chatbot_reply, chatbot_toggle
from modules.admin import (
    get_admin_list, 
    ban_user, 
    unban_user, 
    mute_user, 
    unmute_user, 
    promote_user, 
    get_user_id,
    welcome_toggle
)
from modules.welcome import welcome_member
from modules.logging import log_bot_on, log_group_add
from modules.broadcast import broadcast_handler

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==========================================
# ✶ SET BOT COMMANDS MENU
# ==========================================
async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Bot ko chalu karein ✨"),
        BotCommand("ping", "Bot ki speed check karein ⚡"),
        BotCommand("help", "Saari commands ki list dekhein 📖"),
        BotCommand("id", "Apni ya group ki ID jaanein 🆔"),
        BotCommand("chatbot", "AI Chatbot ON/OFF karein (Admins) 🤖"),
        BotCommand("welcome", "Welcome message ON/OFF karein 🤝"),
        BotCommand("admins", "Group ke admins ki list dekhein 👮"),
        BotCommand("ban", "User ko ban karein (Reply) 🚫"),
        BotCommand("unban", "User ko unban karein 🔓"),
        BotCommand("mute", "User ko mute karein (Reply) 🤫"),
        BotCommand("unmute", "User ko unmute karein 🔊"),
        BotCommand("broadcast", "Sabhi users ko msg bhejin (Owner) 📢"),
    ]
    await application.bot.set_my_commands(commands)

# ==========================================
# ✶ BOT STARTUP SIGNAL
# ==========================================
async def post_init(application):
    """Bot deploy hote hi commands set karega aur notification bhejega"""
    await set_bot_commands(application) # Commands list set karna
    try:
        await log_bot_on(application)
        print("🚀 NATKHAT SYSTEM: ONLINE & COMMANDS SET")
    except Exception as e:
        print(f"Startup Log Error: {e}")

# ==========================================
# ✶ HELPER: CLOSE CALLBACK
# ==========================================
async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()

# ==========================================
# ✶ MAIN APPLICATION ENGINE
# ==========================================
def main():
    # Build Application
    application = ApplicationBuilder().token(Config.BOT_TOKEN).post_init(post_init).build()

    # --- 1. HANDLERS ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("id", get_user_id))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(help_button_callback, pattern="^(help_menu|back_start)$"))
    application.add_handler(CallbackQueryHandler(close_callback, pattern="close_msg"))

    # Admin & Settings
    application.add_handler(CommandHandler("admins", get_admin_list))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("mute", mute_user))
    application.add_handler(CommandHandler("unmute", unmute_user))
    application.add_handler(CommandHandler("promote", promote_user))
    application.add_handler(CommandHandler("chatbot", chatbot_toggle))
    application.add_handler(CommandHandler("welcome", welcome_toggle))

    # Owner & Events
    application.add_handler(CommandHandler("broadcast", broadcast_handler))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    application.add_handler(ChatMemberHandler(log_group_add, ChatMemberHandler.MY_CHAT_MEMBER))

    # --- RUN ---
    print("NATKHAT is Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

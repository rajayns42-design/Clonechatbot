import os  # 'Import' ka 'I' small kar diya (Fixed)
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FIXED IMPORTS (Relative Imports) ---
# Jab aap python -m smartchatbot chalate hain, toh folder ke andar ki files ke liye '.' lagana padta hai
from .config import TOKEN
from .database import get_all_bots
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.cloner import clone_bot, clone_start_handler, anti_nsfw_delete, broadcast_handler, delclone_bot

# Admin Modules
from .modules.admin import ban_user, unban_user, mute_user, unmute_user, promote_user, get_admin_list

# Logging configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Common Handler Registration ---
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL) & ~filters.COMMAND, 
        anti_nsfw_delete
    ), group=1)

# --- Auto Restart Clones Logic ---
async def restart_clones(main_app: Application):
    saved_bots = get_all_bots()
    if not saved_bots:
        logging.info("ℹ️ No cloned bots found in Database.")
        return

    for bot_data in saved_bots:
        token = bot_data["token"]
        try:
            clone_app = Application.builder().token(token).job_queue(True).build()
            register_all_handlers(clone_app)
            await clone_app.initialize()
            await clone_app.start()
            await clone_app.updater.start_polling()
            logging.info(f"✅ Successfully Reconnected: @{bot_data.get('username', 'Bot')}")
        except Exception as e:
            logging.error(f"❌ Reconnect Failed for {token}: {e}")

# --- Main Entry Point ---
def main():
    if not TOKEN:
        logging.error("❌ TOKEN missing in config.py!")
        return

    app = Application.builder().token(TOKEN).job_queue(True).build()
    register_all_handlers(app)

    if app.job_queue:
        # 5 seconds delay to ensure main bot is ready
        app.job_queue.run_once(lambda c: asyncio.create_task(restart_clones(app)), 5)

    print("--- ⚡ NATKHAT AI SYSTEM IS LIVE ⚡ ---")
    app.run_polling()

if __name__ == "__main__":
    main()

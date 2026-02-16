import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Modules Import
from config import TOKEN
from database import get_all_bots
from modules.chatbot import chatbot_reply, chatbot_toggle
from modules.welcome import welcome_toggle, welcome_member
from modules.cloner import clone_bot, clone_start_handler, anti_nsfw_delete

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Common Handler Registration ---
# Ye function Master aur Clone dono mein saari commands ek saath daal dega
def register_all_handlers(app: Application):
    # 1. Start & Clone
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))

    # 2. Chatbot Logic
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

    # 3. Welcome Logic
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # 4. Anti-NSFW (Media Delete) - Group 1 for priority
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL, 
        anti_nsfw_delete
    ), group=1)

# --- Auto Restart Clones ---
async def restart_clones(main_app: Application):
    saved_bots = get_all_bots()
    for bot_data in saved_bots:
        token = bot_data["token"]
        try:
            clone_app = Application.builder().token(token).build()
            
            # Har clone bot ko saari commands dena
            register_all_handlers(clone_app)

            await clone_app.initialize()
            await clone_app.start()
            await clone_app.updater.start_polling()
            logging.info(f"✅ Restarted Clone: @{bot_data['username']}")
        except Exception as e:
            logging.error(f"❌ Failed to restart {token}: {e}")

# --- Main Entry Point ---
def main():
    # Build Master Bot
    app = Application.builder().token(TOKEN).build()

    # Register handlers for Master Bot
    register_all_handlers(app)

    # 5 second baad saare purane clones ko zinda karna
    if app.job_queue:
        app.job_queue.run_once(lambda c: restart_clones(app), 5)

    print("--- ⚡ NATKHAT AI SYSTEM IS LIVE ⚡ ---")
    app.run_polling()

if __name__ == "__main__":
    main()

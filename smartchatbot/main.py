import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Modules Import
from config import TOKEN
from database import get_all_bots
from modules.chatbot import chatbot_reply, chatbot_toggle
from modules.welcome import welcome_toggle, welcome_member
from modules.cloner import clone_bot, clone_start_handler, anti_nsfw_delete

# Admin Modules (Jo humne pehle banaye the)
from modules.admin import ban_user, unban_user, mute_user, unmute_user, promote_user, get_admin_list

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- Common Handler Registration ---
def register_all_handlers(app: Application):
    # 1. Start & Clone
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))

    # 2. Admin Commands (New Added)
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # 3. Chatbot Logic
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

    # 4. Welcome Logic
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # 5. Anti-NSFW (Media Delete)
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
            # Har clone bot ke liye separate job_queue enable karna zaroori hai
            clone_app = Application.builder().token(token).job_queue(True).build()
            
            register_all_handlers(clone_app)

            await clone_app.initialize()
            await clone_app.start()
            # Background polling for clones
            await clone_app.updater.start_polling()
            logging.info(f"✅ Successfully Reconnected: @{bot_data['username']}")
        except Exception as e:
            logging.error(f"❌ Reconnect Failed for {token}: {e}")

# --- Main Entry Point ---
def main():
    # Build Master Bot (job_queue=True is MUST)
    app = Application.builder().token(TOKEN).job_queue(True).build()

    # Register handlers for Master Bot
    register_all_handlers(app)

    # Database se purane clones ko auto-start karna
    if app.job_queue:
        app.job_queue.run_once(lambda c: restart_clones(app), 5)

    print("--- ⚡ NATKHAT AI SYSTEM IS LIVE ⚡ ---")
    print("--- 🤖 ALL CLONES ARE PERSISTENT 🤖 ---")
    
    app.run_polling()

if __name__ == "__main__":
    main()

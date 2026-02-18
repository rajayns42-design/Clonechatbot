import os
import logging
import asyncio
from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- FIXED RELATIVE IMPORTS ---
from .config import TOKEN
from .database import get_all_bots
from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import welcome_toggle, welcome_member
from .modules.cloner import clone_bot, clone_start_handler, anti_nsfw_delete, broadcast_handler, delclone_bot
from .modules.admin import ban_user, unban_user, mute_user, unmute_user, promote_user, get_admin_list
from .modules.ping import ping_handler, ping_callback_handler

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 1. SET COMMANDS MENU ---
async def set_ui_commands(bot):
    """Bot ke niche Menu button mein commands dikhane ke liye."""
    commands = [
        BotCommand("start", "🚀 Start the bot"),
        BotCommand("ping", "⚡ Check speed"),
        BotCommand("clone", "👥 Create a clone"),
        BotCommand("delclone", "🗑 Delete clone"),
        BotCommand("chatbot", "🤖 Toggle Chatbot"),
        BotCommand("welcome", "👋 Toggle Welcome"),
        BotCommand("adminlist", "👮 Show Admins"),
        BotCommand("broadcast", "📢 Broadcast (Owner)")
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logging.error(f"Error setting commands menu: {e}")

# --- 2. REGISTER ALL HANDLERS ---
def register_all_handlers(app: Application):
    """Ye function Master aur Clone dono ke liye commands active karega."""
    
    # Speed & Utility
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="close_ping"))

    # Cloning System
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    
    # Admin Controls
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))
    
    # Broadcast (Sudo)
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    
    # Features (Chatbot & Welcome)
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    
    # Anti-NSFW Delete Logic
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL) & ~filters.COMMAND, 
        anti_nsfw_delete
    ), group=1)

# --- 3. RESTART SAVED CLONES ---
async def restart_clones(main_app: Application):
    """Database se purane bots utha kar unhe restart karega."""
    saved_bots = get_all_bots()
    if not saved_bots:
        logging.info("ℹ️ No cloned bots found to restart.")
        return

    for bot_data in saved_bots:
        token = bot_data["token"]
        try:
            clone_app = Application.builder().token(token).job_queue(True).build()
            
            # Clone bot ka menu set karein
            await set_ui_commands(clone_app.bot)
            
            # Handlers register karein
            register_all_handlers(clone_app)
            
            await clone_app.initialize()
            await clone_app.start()
            await clone_app.updater.start_polling()
            logging.info(f"✅ Clone Active: @{bot_data.get('username', 'Bot')}")
        except Exception as e:
            logging.error(f"❌ Failed to start clone {token}: {e}")

# --- 4. MAIN FUNCTION ---
def main():
    if not TOKEN:
        logging.error("❌ MASTER_TOKEN missing!")
        return

    # Build Master Bot
    app = Application.builder().token(TOKEN).job_queue(True).build()
    
    # Master bot ka menu set karein
    if app.job_queue:
        app.job_queue.run_once(lambda c: asyncio.create_task(set_ui_commands(app.bot)), 1)
        # 5 sec baad clones ko zinda karein
        app.job_queue.run_once(lambda c: asyncio.create_task(restart_clones(app)), 5)

    # Register handlers for Master Bot
    register_all_handlers(app)

    print("--- ⚡ NATKHAT AI IS FULLY OPERATIONAL ⚡ ---")
    app.run_polling()

if __name__ == "__main__":
    main()

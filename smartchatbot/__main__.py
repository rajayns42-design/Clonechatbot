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

# =========================
# IMPORTS
# =========================
from .config import TOKEN, LOGGER_GROUP, OWNER_ID  # OWNER_ID config se uthaya hai
from .database import add_user, get_all_users

from .modules.chatbot import chatbot_reply, chatbot_toggle
from .modules.welcome import (
    welcome_toggle,
    welcome_member,
    master_start,
    help_callback
)
from .modules.admin import (
    ban_user,
    unban_user,
    mute_user,
    unmute_user,
    promote_user,
    get_admin_list
)
from .modules.ping import ping_handler, ping_callback_handler

logging.basicConfig(level=logging.INFO)

# =========================
# OWNER ONLY BROADCAST
# =========================

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Sakht Check: Sirf Owner ID hi allowed hai
    if user_id != int(OWNER_ID):
        await update.message.reply_text("❌ Ye command sirf Bot Owner use kar sakta hai!")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Pehle kisi message (text, photo, etc.) ko reply karein jise broadcast karna hai.")
        return

    msg = update.message.reply_to_message
    users = get_all_users()
    
    sent = 0
    failed = 0
    status_msg = await update.message.reply_text(f"🚀 **Broadcast Started...**\nTarget: {len(users)} users.")

    for uid in users:
        try:
            # copy_message se original message bina 'forward' tag ke jayega
            await context.bot.copy_message(
                chat_id=uid, 
                from_chat_id=msg.chat_id, 
                message_id=msg.message_id
            )
            sent += 1
            await asyncio.sleep(0.05) # Spam protection
        except Exception:
            failed += 1
            
    await status_msg.edit_text(
        f"✅ **Broadcast Finished!**\n\n"
        f"👤 Safal: `{sent}`\n"
        f"❌ Fail: `{failed}`", 
        parse_mode="Markdown"
    )

# =========================
# REGISTER HANDLERS
# =========================

def register_all_handlers(app: Application):
    # Commands
    app.add_handler(CommandHandler("start", master_start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("broadcast", broadcast_handler)) # Owner Only
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))

    # Admin Tools
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # Callbacks & Messages
    app.add_handler(CallbackQueryHandler(master_start, pattern="^start"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help"))
    app.add_handler(CallbackQueryHandler(ping_callback_handler, pattern="^close_ping"))
    
    # Save User ID on every interaction
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, log_user_start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))

    # AI Chatbot Logic
    async def safe_chatbot(update, context):
        try:
            await chatbot_reply(update, context)
        except Exception as e:
            logging.error(f"CHATBOT ERROR: {e}")

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, safe_chatbot))

# =========================
# UTILS & MAIN
# =========================

async def log_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        add_user(update.effective_user.id)

async def post_init(app: Application):
    await app.bot.set_my_commands([
        BotCommand("start", "Start bot"),
        BotCommand("help", "Help menu"),
        BotCommand("ping", "Check speed"),
        BotCommand("broadcast", "Owner Only Broadcast"),
        BotCommand("chatbot", "Toggle AI"),
        BotCommand("adminlist", "Admins list"),
    ])
    try:
        await app.bot.send_message(LOGGER_GROUP, "🟢 Bot is Online (No Cloner Mode)")
    except: pass

def main():
    if not TOKEN: sys.exit("❌ TOKEN missing")
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    register_all_handlers(app)
    print("⚡ BOT RUNNING ⚡")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

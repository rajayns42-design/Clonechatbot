import asyncio
import time
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

from telegram.constants import ChatMemberStatus

# =========================
# IMPORTS (Database & Config)
# =========================
from ..config import OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY
from ..database import (
    add_cloned_bot, 
    remove_cloned_bot, 
    clones_collection,
    users_collection, 
    get_chat_status
)
from .welcome import welcome_member, master_start, help_callback, welcome_toggle
from .admin import (
    ban_user, 
    unban_user, 
    mute_user, 
    unmute_user, 
    promote_user, 
    get_admin_list
)

# =========================
# UNLIMITED 3-API SETUP
# =========================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else: gemini_model = None

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

# =========================
# AI SWITCHING LOGIC (Khatam nahi hoga)
# =========================
async def get_unlimited_ai_reply(text):
    prompt = f"Reply in Hinglish, very short 1 line, friendly chat style: {text}"
    
    # 1. Gemini (First Priority)
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            if response.text: return response.text
        except: pass

    # 2. Groq (Backup 1)
    if groq_client:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            return res.choices[0].message.content
        except: pass

    # 3. Mistral (Backup 2)
    if mistral_client:
        try:
            m_res = mistral_client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return m_res.choices[0].message.content
        except: pass

    return "Bhai sab APIs thak gayi hain, thoda wait kar lo! 🙂"

# =========================
# PING & CHATBOT HANDLERS
# =========================
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    message = await update.message.reply_text("🏓 Pinging...")
    ping_ms = round((time.time() - start_time) * 1000)
    await message.edit_text(f"🚀 **Pong!**\n⚡ Speed: `{ping_ms}ms`")

async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type != "private":
        chat_data = users_collection.find_one({"chat_id": chat_id})
        if not chat_data or not chat_data.get("chatbot_enabled", False): return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    reply = await get_unlimited_ai_reply(update.message.text)
    await update.message.reply_text(reply)

# =========================
# CLONE / DELCLONE WITH INSTRUCTIONS
# =========================
async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        guide = (
            "🚀 **Bot Clone Kaise Karein?**\n\n"
            "1️⃣ @BotFather par jayein aur `/newbot` karein.\n"
            "2️⃣ Apna **API TOKEN** copy karein.\n"
            "3️⃣ Yahan likhein: `/clone <TOKEN>`\n\n"
            "Example: `/clone 12345:AAAbbbCCC`"
        )
        return await update.message.reply_text(guide, parse_mode="Markdown")

    token = context.args[0]
    msg = await update.message.reply_text("⌛ Starting your clone...")
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app)
        await app.initialize()
        await app.start()
        await app.bot.set_my_commands(CLONE_COMMANDS)
        me = await app.bot.get_me()
        add_cloned_bot(update.effective_user.id, token, me.username, me.id)
        await msg.edit_text(f"✅ **Clone Ready!**\nBot: @{me.username}")
    except Exception as e:
        await msg.edit_text(f"❌ Error: Token galat hai!\n`{e}`")

async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🗑 **Likhein:** `/delclone <TOKEN>`")
    
    token = context.args[0]
    data = clones_collection.find_one({"token": token})
    if not data or (update.effective_user.id != data["user_id"] and update.effective_user.id != OWNER_ID):
        return await update.message.reply_text("❌ Ye aapka clone nahi hai!")
    
    remove_cloned_bot(token)
    await update.message.reply_text("🗑 Clone successfully deleted.")

# =========================
# REGISTER HANDLERS (SAB KUCH EK SAATH)
# =========================
def register_all_handlers(app: Application):
    # Start & Help
    app.add_handler(CommandHandler("start", master_start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CallbackQueryHandler(master_start, pattern="start_back"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="help_back"))

    # Admin Suite (Mute, Unmute, Ban, Unban, Promote, Adminlist)
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("adminlist", get_admin_list))

    # Features
    from .chatbot import chatbot_toggle
    app.add_handler(CommandHandler("chatbot", chatbot_toggle))
    app.add_handler(CommandHandler("welcome", welcome_toggle))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))

    # Welcome & Chatbot
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

# =========================
# BOT COMMANDS MENU
# =========================
CLONE_COMMANDS = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Help menu"),
    BotCommand("ping", "Check speed"),
    BotCommand("chatbot", "Toggle AI Chatbot"),
    BotCommand("welcome", "Toggle Welcome"),
    BotCommand("ban", "Ban user"),
    BotCommand("unban", "Unban user"),
    BotCommand("mute", "Mute user"),
    BotCommand("unmute", "Unmute user"),
    BotCommand("promote", "Promote user"),
]

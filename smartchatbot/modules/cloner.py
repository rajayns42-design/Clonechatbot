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

# =========================
# IMPORTS
# =========================
from ..config import OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY
from ..database import (
    add_cloned_bot, 
    remove_cloned_bot, 
    clones_collection,
    users_collection
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
# AI SWITCHING SETUP
# =========================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else: gemini_model = None

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

# =========================
# UNLIMITED AI LOGIC
# =========================
async def get_unlimited_ai_reply(text):
    prompt = f"Reply in Hinglish, very short 1 line: {text}"
    # Switch: Gemini -> Groq -> Mistral
    if gemini_model:
        try:
            r = gemini_model.generate_content(prompt)
            if r.text: return r.text
        except: pass
    if groq_client:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192"
            )
            return res.choices[0].message.content
        except: pass
    if mistral_client:
        try:
            m_res = mistral_client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}]
            )
            return m_res.choices[0].message.content
        except: pass
    return "Net slow hai, fir se bolo! 🙂"

# =========================
# COMMANDS: CLONE & DELCLONE (WITH INSTRUCTIONS)
# =========================

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        text = (
            "🚀 **Bot Clone Kaise Karein?**\n\n"
            "1️⃣ @BotFather par jaakar naya bot banayein.\n"
            "2️⃣ Wahan se **API Token** copy karein.\n"
            "3️⃣ Phir yahan likhein: `/clone <aapka_token>`\n\n"
            "Example: `/clone 12345:AAAbbbCCC`"
        )
        return await update.message.reply_text(text, parse_mode="Markdown")
    
    token = context.args[0]
    msg = await update.message.reply_text("⌛ Starting...")
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app)
        await app.initialize(); await app.start()
        await app.bot.set_my_commands(CLONE_COMMANDS)
        me = await app.bot.get_me()
        add_cloned_bot(update.effective_user.id, token, me.username, me.id)
        await msg.edit_text(f"✅ **Clone Ready!**\nBot: @{me.username}")
    except Exception as e:
        await msg.edit_text(f"❌ Error: Token galat hai!\n`{e}`")

async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        text = (
            "🗑 **Clone Delete Kaise Karein?**\n\n"
            "👉 Likhein: `/delclone <aapka_token>`\n\n"
            "⚠️ **Dhyan dein:** Aap sirf wahi bot delete kar sakte hain jo aapne khud banaya ho."
        )
        return await update.message.reply_text(text, parse_mode="Markdown")
    
    token = context.args[0]
    data = clones_collection.find_one({"token": token})
    if not data or (update.effective_user.id != data["user_id"] and update.effective_user.id != OWNER_ID):
        return await update.message.reply_text("❌ Ye clone aapka nahi hai!")
    
    remove_cloned_bot(token)
    await update.message.reply_text("🗑 **Bot successfully delete kar diya gaya!**")

# =========================
# OTHER HANDLERS
# =========================
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    m = await update.message.reply_text("🏓")
    await m.edit_text(f"🚀 Speed: {round((time.time()-start)*1000)}ms")

async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    chat_id = update.effective_chat.id
    if update.effective_chat.type != "private":
        chat_data = users_collection.find_one({"chat_id": chat_id})
        if not chat_data or not chat_data.get("chatbot_enabled", False): return
    await context.bot.send_chat_action(chat_id, "typing")
    reply = await get_unlimited_ai_reply(update.message.text)
    await update.message.reply_text(reply)

# =========================
# REGISTRATION & MENU
# =========================
def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", master_start))
    app.add_handler(CommandHandler("help", help_callback))
    app.add_handler(CallbackQueryHandler(master_start, pattern="start_back"))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="help_back"))
    
    # Admin Suite
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

    # Msg Handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))

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

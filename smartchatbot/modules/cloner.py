import asyncio
import time
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    ChatPermissions
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from telegram.constants import ChatMemberStatus

# =========================
# IMPORTS
# =========================

from .welcome import welcome_member

try:
    from .admin import ban_user, mute_user, promote_user
except ImportError:
    async def ban_user(update, context):
        await update.message.reply_text("admin module missing")
    async def mute_user(update, context):
        await update.message.reply_text("admin module missing")
    async def promote_user(update, context):
        await update.message.reply_text("admin module missing")

from ..database import (
    add_cloned_bot,
    remove_cloned_bot,
    clones_collection,
    users_collection
)

from ..config import OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY

# LOGGER SAFE IMPORT
try:
    from .logger import log_new_clone
except:
    async def log_new_clone(*a, **k):
        pass


# =========================
# COMMAND MENU
# =========================

CLONE_COMMANDS = [
    BotCommand("start", "Start bot"),
    BotCommand("chaton", "Enable AI Chatbot"),
    BotCommand("chatoff", "Disable AI Chatbot"),
    BotCommand("clone", "Create clone"),
    BotCommand("delclone", "Delete clone"),
    BotCommand("broadcast", "Owner broadcast"),
    BotCommand("ping", "Check speed"),
]

# =========================
# HELPER: ADMIN CHECK
# =========================

async def is_admin(update: Update):
    if update.effective_chat.type == "private":
        return True
    user_status = (await update.effective_chat.get_member(update.effective_user.id)).status
    return user_status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]

# =========================
# AI SETUP
# =========================

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

CLONES = {}

# =========================
# CHATBOT TOGGLE LOGIC
# =========================

async def chatbot_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return await update.message.reply_text("❌ Sirf Admins chatbot on kar sakte hain!")
    
    chat_id = update.effective_chat.id
    users_collection.update_one(
        {"chat_id": chat_id}, 
        {"$set": {"chatbot_enabled": True}}, 
        upsert=True
    )
    await update.message.reply_text("✅ **AI Chatbot ON kar diya gaya hai.**")

async def chatbot_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return await update.message.reply_text("❌ Sirf Admins chatbot off kar sakte hain!")
    
    chat_id = update.effective_chat.id
    users_collection.update_one(
        {"chat_id": chat_id}, 
        {"$set": {"chatbot_enabled": False}}, 
        upsert=True
    )
    await update.message.reply_text("❌ **AI Chatbot OFF kar diya gaya hai.**")

# =========================
# SHORT AI REPLY
# =========================

async def get_ai_reply(text):
    prompt = f"Reply very short 1-2 lines chat style: {text}"
    try:
        if gemini_model:
            r = gemini_model.generate_content(prompt)
            if r and r.text: return r.text[:200]
    except: pass
    return "🙂"

async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    # Database check: Kya is chat mein chatbot ON hai?
    chat_id = update.effective_chat.id
    chat_data = users_collection.find_one({"chat_id": chat_id})
    
    if not chat_data or not chat_data.get("chatbot_enabled", False):
        return

    reply = await get_ai_reply(update.message.text)
    await update.message.reply_text(reply)


# =========================
# START & PING HANDLERS
# =========================

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[InlineKeyboardButton("➕ Add To Group", url=f"https://t.me/{context.bot.username}?startgroup=true")]]
    await update.message.reply_text("Clone ready 🚀", reply_markup=InlineKeyboardMarkup(btn))

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    m = await update.message.reply_text("🏓")
    await m.edit_text(f"{int((time.time()-start)*1000)} ms")

# =========================
# ANTI MEDIA DELETE
# =========================

async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.type == "private":
        return
    if (update.message.photo or update.message.video or update.message.animation or update.message.sticker):
        try: await update.message.delete()
        except: pass

# =========================
# OWNER ONLY BROADCAST
# =========================

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply + /broadcast")

    status = await update.message.reply_text("Broadcasting...")
    targets = [u["user_id"] for u in users_collection.find({}, {"_id": 0, "user_id": 1})]
    ok, bad = 0, 0
    for chat_id in targets:
        try:
            await context.bot.copy_message(chat_id, update.effective_chat.id, update.message.reply_to_message.message_id)
            ok += 1
            await asyncio.sleep(0.4)
        except: bad += 1
    await status.edit_text(f"Done ✅\nSent {ok}\nFail {bad}")

# =========================
# REGISTER HANDLERS
# =========================

def register_all_handlers(app: Application):
    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ping", ping_cmd))

    # Admin & Chatbot Toggle
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("chaton", chatbot_on))
    app.add_handler(CommandHandler("chatoff", chatbot_off))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chatbot_reply))
    app.add_handler(MessageHandler((filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL), anti_nsfw_delete), group=1)

# =========================
# CLONE CREATE & DELETE
# =========================

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Use /clone token")
    token = context.args[0]
    msg = await update.message.reply_text("Starting...")
    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app)
        await app.initialize()
        await app.start()
        await app.bot.set_my_commands(CLONE_COMMANDS)
        me = await app.bot.get_me()
        add_cloned_bot(update.effective_user.id, token, me.username, me.id)
        CLONES[token] = app
        await log_new_clone(context, update.effective_user, token, me.username)
        await msg.edit_text(f"✅ @{me.username}")
    except Exception as e: await msg.edit_text(str(e))

async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    token = context.args[0]
    data = clones_collection.find_one({"token": token})
    if not data or update.effective_user.id not in [data["user_id"], OWNER_ID]: return
    if token in CLONES:
        await CLONES[token].stop()
        del CLONES[token]
    remove_cloned_bot(token)
    await update.message.reply_text("Deleted ✅")

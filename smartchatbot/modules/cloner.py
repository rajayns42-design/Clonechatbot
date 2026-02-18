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

from ..database import add_cloned_bot, remove_cloned_bot, clones_collection
from ..config import OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY

# LOGGER SAFE IMPORT
try:
    from .logger import log_new_clone
except:
    async def log_new_clone(*args, **kwargs):
        pass


# =========================
# COMMAND MENU
# =========================

CLONE_COMMANDS = [
    BotCommand("start", "Start bot"),
    BotCommand("clone", "Create clone"),
    BotCommand("delclone", "Delete clone"),
    BotCommand("ban", "Ban user"),
    BotCommand("mute", "Mute user"),
    BotCommand("promote", "Promote user"),
    BotCommand("ping", "Check speed"),
]


# =========================
# AI SETUP
# =========================

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

CLONES = {}

# =========================
# SHORT AI REPLY
# =========================

async def get_ai_reply(text):

    prompt = f"Reply very short (1–2 lines). User: {text}"

    try:
        if GEMINI_API_KEY:
            r = gemini_model.generate_content(prompt)
            if r and r.text:
                return r.text[:200]
    except:
        pass

    try:
        if groq_client:
            c = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": text}],
                model="llama3-8b-8192",
                max_tokens=80
            )
            return c.choices[0].message.content[:200]
    except:
        pass

    try:
        if mistral_client:
            c = mistral_client.chat.complete(
                model="mistral-tiny",
                messages=[{"role": "user", "content": text}],
                max_tokens=80
            )
            return c.choices[0].message.content[:200]
    except:
        pass

    return "Hmm 🙂"


# =========================
# CHATBOT — UNLIMITED
# =========================

async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    reply = await get_ai_reply(update.message.text)
    await update.message.reply_text(reply)


# =========================
# PING
# =========================

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    start = time.time()
    m = await update.message.reply_text("🏓 Pong...")
    ms = int((time.time() - start) * 1000)
    await m.edit_text(f"⚡ {ms} ms")


# =========================
# START
# =========================

async def clone_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    u = update.effective_user

    btn = [[InlineKeyboardButton(
        "➕ Add To Group",
        url=f"https://t.me/{context.bot.username}?startgroup=true"
    )]]

    await update.message.reply_text(
        f"Hey {u.first_name} ✨\nClone ready 🚀",
        reply_markup=InlineKeyboardMarkup(btn)
    )


# =========================
# ANTI MEDIA DELETE
# =========================

async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    if update.effective_chat.type == "private":
        return

    media = (
        update.message.photo or
        update.message.video or
        update.message.animation or
        update.message.sticker
    )

    if not media:
        return

    try:
        await update.message.delete()
    except:
        pass


# =========================
# HANDLERS REGISTER
# =========================

def register_all_handlers(app: Application):

    app.add_handler(CommandHandler("start", clone_start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))

    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("promote", promote_user))
    app.add_handler(CommandHandler("ping", ping_cmd))

    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        welcome_member
    ))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chatbot_reply
    ))

    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Sticker.ALL),
        anti_nsfw_delete
    ), group=1)


# =========================
# CLONE CREATE
# =========================

async def clone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        return await update.message.reply_text("Use: /clone <bot_token>")

    token = context.args[0]
    msg = await update.message.reply_text("Starting clone...")

    try:
        app = Application.builder().token(token).build()
        register_all_handlers(app)

        await app.initialize()
        await app.start()

        await app.bot.set_my_commands(CLONE_COMMANDS)

        bot_info = await app.bot.get_me()

        add_cloned_bot(
            update.effective_user.id,
            token,
            bot_info.username,
            bot_info.id
        )

        CLONES[token] = app

        await log_new_clone(
            context,
            update.effective_user,
            token,
            bot_info.username
        )

        await msg.edit_text(f"✅ @{bot_info.username} active")

    except Exception as e:
        await msg.edit_text(f"Clone failed:\n{e}")


# =========================
# DELETE CLONE — OWNER ONLY
# =========================

async def delclone_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        return await update.message.reply_text("Use: /delclone <token>")

    token = context.args[0]
    data = clones_collection.find_one({"token": token})

    if not data:
        return await update.message.reply_text("Clone not found")

    if (
        update.effective_user.id != data["user_id"]
        and update.effective_user.id != OWNER_ID
    ):
        return await update.message.reply_text("Only clone owner can delete")

    if token in CLONES:
        await CLONES[token].stop()
        del CLONES[token]

    remove_cloned_bot(token)

    await update.message.reply_text("🗑️ Clone removed")

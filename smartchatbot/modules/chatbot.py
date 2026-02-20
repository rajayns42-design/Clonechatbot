import random
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
from telegram import Update
from telegram.ext import ContextTypes
from ..database import get_chat_status, set_chat_status
from ..config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# API Clients Setup
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash") 
groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# User Memory (Sirf pehli baar naam lene ke liye)
replied_users = set()

SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli ladki hai. "
    "Rule: Reply ONLY in 2 to 3 Hinglish words + 1 emoji. "
    "Very short and sweet. No quotes."
)

# =========================
# TOGGLE COMMAND (/chatbot on/off)
# =========================
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        return await update.message.reply_text("<blockquote>DM mein main hamesha taiyar hu! 😉</blockquote>", parse_mode="HTML")

    # Admin/Owner check
    member = await context.bot.get_chat_member(chat.id, user.id)
    if member.status not in ["administrator", "creator"] and user.id != int(OWNER_ID):
        return await update.message.reply_text("<blockquote>❌ Sirf Admins hi mujhe on/off kar sakte hain!</blockquote>", parse_mode="HTML")

    if not context.args:
        return await update.message.reply_text("<blockquote>Usey: /chatbot on ya /chatbot off</blockquote>", parse_mode="HTML")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("<blockquote>✅ Chatbot ON! Ab har message pe baatein hogi. 😉</blockquote>", parse_mode="HTML")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("<blockquote>📴 Chatbot OFF. Phir milenge! 🥺</blockquote>", parse_mode="HTML")

# =========================
# AUTO-SWITCH ENGINE (The Triple Switch)
# =========================
async def get_ai_reply(text: str):
    # SWITCH 1: GEMINI
    try:
        response = gemini_model.generate_content(f"{SYSTEM_PROMPT}\nUser: {text}")
        if response and response.text:
            return response.text.replace('"', '').strip()
    except: pass

    # SWITCH 2: GROQ
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}],
            max_tokens=15
        )
        return r.choices[0].message.content.replace('"', '').strip()
    except: pass

    # SWITCH 3: MISTRAL
    try:
        r = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}]
        )
        return r.choices[0].message.content.replace('"', '').strip()
    except: pass

    return None

# =========================
# MESSAGE HANDLER
# =========================
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.message.text.startswith("/"): return

    chat = update.effective_chat
    user = update.effective_user

    # Group check (Toggle status check yahan ho raha hai)
    if chat.type != "private" and not get_chat_status(chat.id):
        return

    reply = await get_ai_reply(update.message.text)

    if reply:
        if user.id not in replied_users:
            final_msg = f"{user.first_name}, {reply}"
            replied_users.add(user.id)
        else:
            final_msg = reply

        try:
            await context.bot.send_chat_action(chat_id=chat.id, action="typing")
            await update.message.reply_text(final_msg)
        except: pass

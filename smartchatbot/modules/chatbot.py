import random
import google.generativeai as genai # Fixed import
from groq import Groq
from mistralai import Mistral

from telegram import Update
from telegram.ext import ContextTypes

from ..database import get_chat_status, set_chat_status
from ..config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    MISTRAL_API_KEY,
    OWNER_ID
)

# =========================
# AI CLIENTS SETUP (FIXED)
# =========================
genai.configure(api_key=GEMINI_API_KEY)
# Gemini model setup
gemini_model = genai.GenerativeModel("gemini-1.5-flash") 

groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli ladki hai. "
    "Reply only 3 to 5 Hinglish words with 1 emoji. No quotes."
)

# =========================
# UTILS
# =========================
def clean_for_telegram(text: str):
    return (
        text.replace('"', '').replace("'", "").replace("`", "")
        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .strip()
    )

# =========================
# AI CALLS (FIXED LOGIC)
# =========================
async def ask_gemini(user_text):
    try:
        # Fixed Gemini Calling Method
        response = gemini_model.generate_content(f"{SYSTEM_PROMPT}\nUser: {user_text}")
        if response.text:
            return clean_for_telegram(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

async def ask_groq(user_text):
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": user_text}],
            max_tokens=25,
            temperature=0.8
        )
        return clean_for_telegram(r.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return None

# =========================
# MASTER AI ENGINE
# =========================
async def get_ai_reply(text: str):
    # Pehle Gemini try karo
    reply = await ask_gemini(text)
    if reply: return reply
    
    # Fail hua toh Groq try karo
    reply = await ask_groq(text)
    if reply: return reply
    
    # Sab fail toh fallback
    return random.choice(["Haan bol 😏", "Sun rahi hu 😌", "Acha ji 😜", "Hmm sahi hai 😅"])

# =========================
# CHATBOT TOGGLE
# =========================
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        return await update.message.reply_text("DM mein toh main hamesha taiyar hu! 😉")

    # Admin check
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"] and user.id != int(OWNER_ID):
            return await update.message.reply_text("❌ Sirf Admins hi mujhe on/off kar sakte hain!")
    except: return

    if not context.args:
        return await update.message.reply_text("Usey: /chatbot on ya /chatbot off")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("✅ **Chatbot ON!** Ab baatein shuru karein? 😉", parse_mode="Markdown")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("📴 **Chatbot OFF.** Phir milenge! 🥺", parse_mode="Markdown")

# =========================
# MESSAGE HANDLER (FINAL FIX)
# =========================
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.message.text.startswith("/"): return

    chat = update.effective_chat
    # DM check ya Group ON check
    if chat.type != "private" and not get_chat_status(chat.id):
        return

    # Trigger conditions: DM, Reply to Bot, or Tagging Bot
    is_reply_to_bot = (update.message.reply_to_message and 
                       update.message.reply_to_message.from_user.id == context.bot.id)
    is_tagged = f"@{context.bot.username}" in update.message.text

    if chat.type == "private" or is_reply_to_bot or is_tagged:
        await context.bot.send_chat_action(chat_id=chat.id, action="typing")
        user_msg = update.message.text.replace(f"@{context.bot.username}", "").strip()
        
        reply = await get_ai_reply(user_msg)
        await update.message.reply_text(reply)

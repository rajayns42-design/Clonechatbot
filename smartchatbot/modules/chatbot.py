import random
import google.generativeai as genai
from groq import Groq
from mistralai import Mistral
from telegram import Update
from telegram.ext import ContextTypes
from ..database import get_chat_status, set_chat_status
from ..config import GEMINI_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OWNER_ID

# --- API Clients Setup ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash") 
groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# --- Global Memory ---
# Ye har chat ki pichli 5-6 baatein yaad rakhega
chat_memory = {}

SYSTEM_PROMPT = (
    "Tera naam NATKHAT hai. Tu ek chulbuli aur shararati ladki hai. "
    "Rules: \n"
    "1. Reply ONLY in 2 to 3 Hinglish words + 1 emoji. \n"
    "2. Kabhi bhi purana reply repeat mat karna. \n"
    "3. Human-like baatein kar, robotic nahi. \n"
    "4. No quotes, no formal Hindi. Sirf tapori ya dosti wali Hinglish."
)

# =========================
# AUTO-SWITCH ENGINE (With Memory)
# =========================
async def get_ai_reply(chat_id, text: str):
    # History fetch karna
    if chat_id not in chat_memory:
        chat_memory[chat_id] = []
    
    # Context taiyar karna
    history_str = "\n".join(chat_memory[chat_id][-6:])
    full_prompt = f"{SYSTEM_PROMPT}\n\nRecent History:\n{history_str}\n\nUser: {text}\nNATKHAT:"

    # --- SWITCH 1: GEMINI ---
    try:
        response = gemini_model.generate_content(full_prompt)
        if response and response.text:
            reply = response.text.replace('"', '').strip()
            save_to_memory(chat_id, text, reply)
            return reply
    except: pass

    # --- SWITCH 2: GROQ ---
    try:
        r = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"History: {history_str}\nNow User says: {text}"}
            ],
            max_tokens=20
        )
        reply = r.choices[0].message.content.replace('"', '').strip()
        save_to_memory(chat_id, text, reply)
        return reply
    except: pass

    # --- SWITCH 3: MISTRAL ---
    try:
        r = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context: {history_str}\nUser: {text}"}
            ]
        )
        reply = r.choices[0].message.content.replace('"', '').strip()
        save_to_memory(chat_id, text, reply)
        return reply
    except: pass

    return "Mood nahi hai! 🙄"

def save_to_memory(chat_id, user_msg, bot_msg):
    chat_memory[chat_id].append(f"User: {user_msg}")
    chat_memory[chat_id].append(f"NATKHAT: {bot_msg}")
    # Memory saaf rakhne ke liye sirf last 10 lines rakho
    if len(chat_memory[chat_id]) > 10:
        chat_memory[chat_id] = chat_memory[chat_id][-10:]

# =========================
# TOGGLE COMMAND (/chatbot on/off)
# =========================
async def chatbot_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        return await update.message.reply_text("<blockquote>Main hamesha on hu yahan! 😉</blockquote>", parse_mode="HTML")

    # Admin check
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"] and str(user.id) != str(OWNER_ID):
            return await update.message.reply_text("<blockquote>❌ Sirf Admins hi mujhe handle kar sakte hain!</blockquote>", parse_mode="HTML")
    except: pass

    if not context.args:
        return await update.message.reply_text("<blockquote>Usey: /chatbot on ya off</blockquote>", parse_mode="HTML")

    action = context.args[0].lower()
    if action == "on":
        set_chat_status(chat.id, True)
        await update.message.reply_text("<blockquote>✅ NATKHAT Active! Ab mazaa aayega. 😉</blockquote>", parse_mode="HTML")
    elif action == "off":
        set_chat_status(chat.id, False)
        await update.message.reply_text("<blockquote>📴 Main sone ja rahi hu. Bye! 🥺</blockquote>", parse_mode="HTML")

# =========================
# MESSAGE HANDLER
# =========================
async def chatbot_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.message.text.startswith("/"): return

    chat = update.effective_chat
    user = update.effective_user

    # Status check (Database se)
    if chat.type != "private" and not get_chat_status(chat.id):
        return

    # Typing action dikhane ke liye
    await context.bot.send_chat_action(chat_id=chat.id, action="typing")
    
    # API se reply mangwao (Chat ID ke sath for memory)
    reply = await get_ai_reply(chat.id, update.message.text)

    if reply:
        await update.message.reply_text(reply)
